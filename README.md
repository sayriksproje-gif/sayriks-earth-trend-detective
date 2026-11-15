# Earth Trend Detective (NASA Space Apps Challenge 2026)

**SAYRİKS Space Technological Research** tarafından geliştirilen, NASA açık verilerini kullanarak seçili lokasyonlarda iklim göstergelerindeki **trend ve anomalileri** analiz eden açık kaynaklı Streamlit uygulaması.

## Proje Özeti
- **Amaç:** Zaman serisi iklim verilerinde eğilim (trend) ve sapmaları (anomali) hızlı, anlaşılır ve yorumlanabilir şekilde göstermek.
- **Etki:** Öğrenciler, yerel planlayıcılar ve araştırmacılar için erken içgörü ve önceliklendirme desteği sağlamak.
- **Odak kriterleri:** Etki, Yaratıcılık, Gerçekçilik, Geçerlilik, Sunum.

## Öne Çıkan Özellikler
- **Gerçek veri modu:** NASA POWER Daily Point API üzerinden günlük zaman serisi çekimi (`T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `PRECTOTCORR`).
- **Offline/Demo modu:** Ağ/API erişimi olmadığında etiketli simülasyon (fallback) ile arayüz ve akış testi.
- **İstatistiksel analiz:** Ortalama/min/max/std, lineer trend eğimi, R² ve **p-value**; anlamlılık yorumu.
- **Görselleştirme:** Günlük/yıllık seri grafikleri, trend çizgisi, yıllık anomali grafiği, harita görünümü.
- **Karşılaştırma:** Hazır lokasyonlarda hızlı trend taraması ve sıralama tablosu.
- **Veri dışa aktarım:** Filtrelenmiş veriyi CSV olarak indirme.
- **Metodoloji & Kaynaklar:** Veri kaynağı, yöntem, varsayım/sınırlılık ve atıf bilgileri.
- **Sunum sekmesi:** Uygulama içinde 7 sayfalık jüri sunum akışı (konuşma notları ve demo adımları).

## Proje Yapısı
```text
.
├── app.py                  # Ana Streamlit uygulaması (sekmeler + sunum sayfası)
├── utils/
│   ├── __init__.py
│   ├── data_fetcher.py     # NASA POWER veri çekme ve ön işleme
│   └── analyzer.py         # İstatistik ve trend/anlamlılık analizi
├── .streamlit/config.toml  # Tema ayarları
├── archive/                # Önceki app sürümleri (app001-app007)
├── requirements.txt
├── README.md
├── SUNUM.md                # Yazılı sunum metni (7+ bölüm)
├── LICENSE
├── baslat.bat
└── baslat.sh
```

## Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.10+
- İnternet erişimi (NASA POWER gerçek veri modu için)

### Windows
```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
veya `baslat.bat`

### Linux / WSL
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```
veya `bash baslat.sh`

## Metodoloji (Kısa)
- **Veri:** NASA POWER Daily API (`community=RE`, günlük nokta zaman serisi).
- **Ön işleme:** Tarih/sayısal dönüşüm, eksik/geçersiz değer ayıklama (örn. -999).
- **Analiz:** Temel istatistikler + lineer regresyon (`scipy.stats.linregress`) ile eğim, R², p-value.
- **Yorum:** p-value ve örneklem büyüklüğüne göre anlamlılık yorumu; sonuçlar yöntemsel sınırlılıklarla birlikte sunulur.
- **Anomali:** Yıllık ortalamaların dönem ortalamasına göre sapması.

## Veri Kaynakları ve Atıf
- NASA POWER Project: https://power.larc.nasa.gov/
- NASA Space Apps Challenge: https://www.spaceappschallenge.org/
- NASA Space Apps (GitHub): https://github.com/nasa/spaceapps
- Challenge Details/Resources kapsamında referans verilen araç/kaynaklar: Giovanni, AppEEARS, CDO, KNMI Climate Explorer, istatistiksel anlamlılık/trend test rehberleri, SWOT/RCM vb. (kullanım/karşılaştırma durumuna göre metodolojide belirtilir).

## Sınırlılıklar
- Tek lokasyon/parametre analizi tüm iklim sistemini temsil etmez.
- Model/uydu tabanlı veri ürünleri yer gözlemleriyle farklılık gösterebilir.
- Lineer trend ve p-value yorumu; otokorelasyon, veri boşlukları ve model varsayımlarına duyarlıdır.
- Simülasyon modu bilimsel gözlem değildir (yalnızca demo/fallback).
- Çıktılar erken içgörü amaçlıdır; kritik kararlar için uzman değerlendirmesi gerekir.

## Uyum ve Notlar
- Bu proje **NASA tarafından desteklenmemekte veya onaylanmamaktadır**. NASA açık verilerini kullanır.
- NASA Space Apps Challenge **Terms & Conditions** ve davranış kurallarına uygun hazırlanmalıdır.
- Katkıda bulunurken veri kullanımı, atıf ve paylaşım koşullarına uyulmalıdır.

## Lisans
Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.
