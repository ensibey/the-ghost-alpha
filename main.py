import os
import json
import time
import concurrent.futures
from crewai import Crew, Process, Task
from dotenv import load_dotenv

# Database & Local Export
from core.database import save_to_db
from core.local_exporter import export_to_local_csv
from core.notifier import send_telegram_signal

# Agents & Schemas (Function Wrappers)
from agents.signal_bot import create_signal_bot
from agents.dev_bot import create_dev_bot
from agents.market_bot import create_market_bot
from agents.analyzer_agent import create_analyzer_agent
from agents.strategist_agent import create_strategist_agent
from agents.writer_agent import create_writer_agent
from agents.models import IntelligenceOutput

def make_intelligence_callback(category_name, source_url):
    """Her URL'ye özel ayrıştırılmış bağımsız callback döngüsü."""
    def handle_intelligence_output(task_output):
        if task_output.pydantic:
            data = task_output.pydantic.dict()
            if data.get("firsat_tipi") is not None and data.get("seviye") is not None:
                print(f"\n[🚀 BAŞARILI] {category_name} -> Özel Sinyal Yakalandı: Seviye {data['seviye']}")
                export_to_local_csv(category_name, data)
                save_to_db("ai_filtered_opportunities", {"data": data})
                
                # Sadece Seviye 5 ve üstü fırsatları Telegram'a at (Gürültü engelleme)
                if int(data.get("seviye", 0)) >= 5:
                    send_telegram_signal(category_name, data)
            else:
                print(f"[-] Null (Çöp) veri elendi -> {source_url}")
    return handle_intelligence_output

def process_single_target(payload):
    """
    Bu fonksiyon ThreadPoolExecutor tarafından çağrılır. Her URL için BAĞIMSIZ 
    bir 'Mini-Özel-Ajan Ekibi (Micro Crew)' inşa eder. Bu sayede RAM izolasyonu 
    sağlanır ve Playwright Chromium sekmeleri birbirine karışmaz (Thread-Safe).
    """
    url, category_name, bot_factory = payload
    
    # 1. Kendi izole süreçleri için Ajan yaratım (Her Thread kendi ajanını kullanır)
    special_bot = bot_factory()
    ai_filter = create_analyzer_agent()
    ai_strategist = create_strategist_agent()
    ai_writer = create_writer_agent()
    
    # 2. Spesifik Görev Ataması
    scrape_task = Task(
        description=f"Visit explicitly '{url}' and extract all crucial latest information, text, prices or trends.", 
        expected_output=f"Raw text dump representing the page content from {url}", 
        agent=special_bot
    )
    
    filter_task = Task(
        description=(
            "Sen The Ghost Alpha zeka çekirdeğisin. Aşağıdaki profesyonel pazar verisini analiz et.\n"
            "Gelen veriden pazarın en sıcak ve kârlı noktalarını (yazılım trendleri, on-chain sinyalleri, arbitraj) bul.\n"
            "Çöp veriyi kesinlikle elenmeli. Sadece yüksek kaliteli olanları bırak."
        ),
        expected_output="Filtered quality signal text or 'null'.",
        agent=ai_filter
    )
    
    strategy_task = Task(
        description=(
            "Eğer veri kaliteliyse (null değilse), bu fırsattan nasıl para kazanılacağına dair "
            "kesin ve etkili bir 'Pazar Stratejisi' (Monetization Strategy) geliştir. "
            "Domain alımı, içerik üretimi, satış kanalı önerisi veya yatırım tavsiyesi ver."
        ),
        expected_output="A concrete and actionable strategy text.",
        agent=ai_strategist
    )
    
    packaging_task = Task(
        description=(
            "Strateji ve sinyal verisini al. Bunları 'AI-Ready' bir pazarlama metni haline getir. "
            "Ayrıca tüm veriyi (Fırsat Tipi, Seviye, Neden, Kaynak URL, Platform, Strateji, Pazarlama Metni) "
            "tam bir JSON objesi olarak yapılandır."
        ),
        expected_output="Full JSON object with Strategy and Marketing Content.",
        agent=ai_writer,
        output_pydantic=IntelligenceOutput,
        callback=make_intelligence_callback(category_name, url)
    )
    
    packaging_task.context = [scrape_task, filter_task, strategy_task]
    
    # 3. Yalnızca bu URL için Mikro Ekip (Mini Crew) - Sequential Process (Filter -> Strat -> Write)
    mini_crew = Crew(
        agents=[special_bot, ai_filter, ai_strategist, ai_writer],
        tasks=[scrape_task, filter_task, strategy_task, packaging_task],
        process=Process.sequential,
        verbose=False 
    )
    
    print(f"[*] Thread Başladı: {category_name} -> {url}")
    try:
        mini_crew.kickoff()
    except Exception as e:
        print(f"[!] Hata Alındı ({url}): {e}")

def main():
    print("==================================================")
    print(" THE GHOST ALPHA - CONTINUOUS AUTONOMOUS ENGINE")
    print("==================================================")
    load_dotenv()
    
    # ----------------- DEVELOPE HEDEF HAVUZLARI (MASSIVE & PRO SCALE) -----------------
    # 2026 Model: Sadece site gezmiyoruz, on-chain ve derin pazar süzgecine iniyoruz.
    signal_targets = [
        "https://news.ycombinator.com/",
        "https://old.reddit.com/r/CryptoCurrency/new/",
        "https://old.reddit.com/r/WallStreetBets/new/",
        "https://old.reddit.com/r/Solana/new/",
        "https://old.reddit.com/r/Entrepreneur/",
    ]
    
    dev_targets = [
        "https://github.com/search?q=stars:>1000+s:updated&type=repositories",
        "https://github.com/search?q=stars:>5000+s:updated&type=repositories",
        "https://github.com/trending/python?since=daily",
        "https://huggingface.co/papers"
    ]
    
    market_targets = [
        "https://pump.fun/board",
        "https://dexscreener.com/gainers",
        "https://www.ebay.com/sch/i.html?_nkw=rtx+4090&_sop=10",
        "https://www.ebay.com/sch/i.html?_nkw=macbook+pro+m3+max&_sop=10"
    ]
    
    # Savaş Alanı Planlaması (Payloads)
    # Hangi URL, Hangi Kategori İsmiyle ve Hangi Bot Fonksiyonu ile çalıştırılacak?
    payloads = []
    for url in signal_targets:
        payloads.append((url, "Piyasa_Sinyalleri", create_signal_bot))
    for url in dev_targets:
        payloads.append((url, "Gelistirici_Trendleri", create_dev_bot))
    for url in market_targets:
        payloads.append((url, "Arbitraj_Sinyalleri", create_market_bot))
        
    total_urls = len(payloads)
    print(f"[#] Toplam Keşfedilecek Kaynak: {total_urls}")
    print(f"[#] Bilgisayarı koruma (RAM) sınırı: Aynı Asenkron Anda 5 Sekme\n")
    
    # --- ZAMAN YÖNETIMI VE SÜREKLI DÖNGÜ ---
    start_time = time.time()
    max_duration = (5 * 3600) + (45 * 60) # 5 Saat 45 Dakika limiti
    cycle_count = 1
    sleep_duration_seconds = 180 # 3 dakika dinlenme koruması (IP ban yememek için)
    
    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        # GitHub Actions güvenlik limiti kontrolü (Max 6 saate takılmamak için önceden çık)
        if elapsed > max_duration:
            print(f"\n[SİSTEM UYARISI] 5 Saat 45 Dakikalık güvenli çalışma sınırı aşıldı! (Geçen süre: {int(elapsed/60)} dk)")
            print("[SİSTEM UYARISI] GitHub Action'ın kaza ile kapanmaması için sistem kendini GÜVENLİ ve başarılı bir şekilde DURDURUYOR.")
            print("[SİSTEM UYARISI] Bir sonraki Cron tetikleyicisi bekleniyor...")
            break
            
        print(f"\n==================================================")
        print(f" [🔥] TARAMA DÖNGÜSÜ {cycle_count} BAŞLIYOR... (Kalan Güvenli Süre: {int((max_duration-elapsed)/60)} dk)")
        print(f"==================================================")

        # Asenkron İşçi Havuzunu (Thread Pool) tetikle!
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            list(executor.map(process_single_target, payloads))
            
        print(f"\n[!] Döngü {cycle_count} Tamamlandı.")
        print(f"[*] Hedef sitelerin siber saldırı algılamaması için {int(sleep_duration_seconds/60)} dakika ZORUNLU DİNLENME moduna geçiliyor zzz...")
        time.sleep(sleep_duration_seconds)
        cycle_count += 1
        
    print("\n==================================================")
    print(" GHOST ALPHA MOTORU GÜVENLİ OLARAK KAPANDI.")
    print("==================================================")

if __name__ == "__main__":
    main()
