import React, { useEffect, useState } from 'react';
import { supabase } from './supabaseClient';
import './index.css';

function OpportunityCard({ opp, index }) {
  const level = opp.data.seviye || 0;
  let levelClass = 'level-low';
  let badgeClass = 'badge-low';
  
  if (level >= 8) {
    levelClass = 'level-high';
    badgeClass = 'badge-high';
  } else if (level >= 5) {
    levelClass = 'level-medium';
    badgeClass = 'badge-medium';
  }

  const animStyle = { animationDelay: `${index * 0.15}s`, opacity: 0 };
  const platform = opp.data.platform_ismi || 'Web';
  const sourceUrl = opp.data.kaynak_url && opp.data.kaynak_url !== 'Bilinmiyor' 
                    ? opp.data.kaynak_url : null;

  return (
    <div className={`glass-panel opp-card ${levelClass} animate-fade-in`} style={animStyle}>
      <div className="opp-header">
        <h3 className="opp-title">{opp.data.firsat_tipi || 'Bilinmeyen Fırsat'}</h3>
        <span className={`opp-badge ${badgeClass}`}>Seviye {level}</span>
      </div>
      <p className="opp-reason">{opp.data.neden}</p>
      
      <div className="opp-meta">
        <span className="platform-tag">{platform}</span>
        {sourceUrl ? (
          <a href={sourceUrl.startsWith('http') ? sourceUrl : `https://${sourceUrl}`} target="_blank" rel="noopener noreferrer" className="source-link">
            &#128279; Kaynağa Git
          </a>
        ) : (
          <span className="no-source">Kaynak Link Yok</span>
        )}
      </div>

      <div className="opp-footer">
        <span>Gelişmiş AI Analizi</span>
        <span>{new Date(opp.created_at || Date.now()).toLocaleDateString('tr-TR')}</span>
      </div>
    </div>
  );
}

function App() {
  const [opportunities, setOpportunities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOpportunities();
    const channel = supabase
      .channel('public:ai_filtered_opportunities')
      .on('postgres_changes', { event: 'INSERT', schema: 'public', table: 'ai_filtered_opportunities' }, payload => {
        setOpportunities(current => [payload.new, ...current]);
      })
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, []);

  async function fetchOpportunities() {
    try {
      const { data, error } = await supabase
        .from('ai_filtered_opportunities')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(20);

      if (error) {
        setOpportunities([
           { id: 1, data: { firsat_tipi: "Arbitraj: RTX 4090", seviye: 9, neden: "eBay üzerinde liste fiyatı piyasanın %30 altında olan 2 ilan tespit edildi.", platform_ismi: "eBay", kaynak_url: "https://www.ebay.com/sch/i.html?_nkw=rtx+4090" } },
           { id: 2, data: { firsat_tipi: "Yükselen Repo: AutoGPT", seviye: 7, neden: "Github'da son 24 saatte yıldız sayısı %500 arttı. Yeni framework dalgası.", platform_ismi: "GitHub", kaynak_url: "https://github.com/trending/python?since=daily" } },
           { id: 3, data: { firsat_tipi: "Reddit Leak: Yeni Kripto", seviye: 4, neden: "r/CryptoCurrency sub'ında gizli bir airdrop duyurusu yayıldı.", platform_ismi: "Reddit", kaynak_url: "https://old.reddit.com/r/programming/" } }
        ]);
      } else {
        setOpportunities(data || []);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  // Fonksiyon: İndirme İşlemi - Müşteriye Datayı Satiyoruz.
  const handleExportCSV = () => {
    if (opportunities.length === 0) return;
    
    // Basit bir CSV oluşturucu
    const headers = ["Fırsat Tipi", "Seviye", "Neden", "Platform", "Orijinal Kaynak", "Tarih"];
    const rows = opportunities.map(opp => [
      `"${opp.data.firsat_tipi || ''}"`,
      opp.data.seviye || '',
      `"${(opp.data.neden || '').replace(/"/g, '""')}"`,
      `"${opp.data.platform_ismi || ''}"`,
      `"${opp.data.kaynak_url || ''}"`,
      new Date(opp.created_at || Date.now()).toLocaleDateString('tr-TR')
    ]);
    
    const csvContent = "data:text/csv;charset=utf-8," 
                       + headers.join(",") + "\n" 
                       + rows.map(e => e.join(",")).join("\n");
                       
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `ghost_alpha_data_feed_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="dashboard-container">
      <header className="header animate-fade-in">
        <div className="header-topline">
          <div></div>
          <button onClick={handleExportCSV} className="export-btn">⬇ Export to CSV</button>
        </div>
        <h1>The Ghost Alpha</h1>
        <p>Premium Market Signals & Arbitrage Data Feed</p>
      </header>

      {loading ? (
        <div className="loader">Veri Ağı Taranıyor...</div>
      ) : (
        <div className="opportunities-grid">
          {opportunities.map((opp, idx) => (
            <OpportunityCard key={opp.id || idx} opp={opp} index={idx} />
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
