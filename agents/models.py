from pydantic import BaseModel, Field
from typing import Optional

class IntelligenceOutput(BaseModel):
    """
    Kullanıcının belirlediği filtreleme şeması.
    Eğer data çöp ise LLM bu alanları None/Null bırakır veya seviyeyi 0 yapar.
    """
    firsat_tipi: Optional[str] = Field(
        default=None, 
        description="Fırsatın türü (Örn: 'yeni ürün', 'yükselen trend', 'arbitraj'). Eğer içerik çöp (fırsat yok) ise null/None bırakın."
    )
    seviye: Optional[int] = Field(
        default=None, 
        description="Fırsatın büyüklük seviyesi (1-10 arası). Eğer içerik çöp ise null/None bırakın.",
        ge=1, le=10
    )
    neden: Optional[str] = Field(
        default=None, 
        description="Neden bu bir fırsat olarak görülüyor? Kısaca açıklayın. İçerik çöp ise null/None bırakın."
    )
    kaynak_url: Optional[str] = Field(
        default=None,
        description="Bu verinin çekildiği tam URL adresi (Orijinal Link). Satışta kanıt için gereklidir."
    )
    platform_ismi: Optional[str] = Field(
        default=None,
        description="Verinin geldiği ana platformun adı (Örn: Reddit, Github, eBay, X). Baş harfi büyük olsun."
    )
    strateji: Optional[str] = Field(
        default=None,
        description="Bu veriden nasıl para kazanılır? Stratejist ajanı tarafından doldurulur."
    )
    pazarlama_metni: Optional[str] = Field(
        default=None,
        description="Verinin satışını kolaylaştıracak AI-Ready pazarlama metni veya blog yazısı."
    )
