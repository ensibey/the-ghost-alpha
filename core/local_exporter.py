import os
import csv
from datetime import datetime

# Hedef olarak hiçbir alt klasör olmadan DOĞRUDAN kullanıcının Masaüstünü ayarlıyoruz
DESKTOP_DIR = os.path.join(os.path.expanduser("~"), "Desktop")

def ensure_dir_exists():
    """Hedef veriseti klasörünün masaüstünde var olduğundan emin olur."""
    if not os.path.exists(DESKTOP_DIR):
        try:
            os.makedirs(DESKTOP_DIR)
        except Exception as e:
            print(f"Klasör oluşturulamadı: {e}")

def export_to_local_csv(category_name, data_dict):
    """
    Belirli bir kategoriye (Örn: Sinyaller, Geliştirici, Arbitraj) ait fırsat 
    verisini Masaüstündeki CSV dosyasına yazar (Append usulüyle sütun atlamadan).
    """
    ensure_dir_exists()
    
    # Tarihe göre günlük yazar (Örn: Sinyaller_2026-04-12.csv)
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{category_name}_{date_str}.csv"
    filepath = os.path.join(DESKTOP_DIR, filename)
    
    file_exists = os.path.isfile(filepath)
    
    # Dışa aktarılacak yapılandırılmış sütun sıralaması
    headers = ["Kategori", "Tarih", "Seviye", "Platform", "Firsat_Tipi", "Neden", "Kaynak_URL", "Strateji", "Pazarlama_Metni"]
    
    try:
        with open(filepath, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Eğer dosya yeni açılıyorsa ilk satıra başlıkları bas
            if not file_exists:
                writer.writerow(headers)
                
            writer.writerow([
                category_name,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                data_dict.get("seviye", ""),
                data_dict.get("platform_ismi", "Bilinmiyor"),
                data_dict.get("firsat_tipi", ""),
                data_dict.get("neden", ""),
                data_dict.get("kaynak_url", ""),
                data_dict.get("strateji", ""),
                data_dict.get("pazarlama_metni", "")
            ])
            print(f"[LOCAL DB] Fırsat {category_name} CSV dosyasına (Masaüstü) işlendi.")
            
    except Exception as e:
        print(f"[-] CSV'ye yazarken yerel kayıt hatası: {e}")
