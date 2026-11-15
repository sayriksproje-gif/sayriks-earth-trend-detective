# Proje Dosya Yapısı

SAYRİKS Space Technological Research ekibinin geliştirdiği minimalist, modüler ve sıfır maliyetli proje dizin yapısı:

sayriks-earth-trend-detective/
│
├── .gitignore               # Git tarafından yoksayılacak dosyalar (venv, cache vb.)
├── README.md                # Proje genel tanımı, kurulum ve donanım/yazılım gereksinimleri
├── TODO.md                  # 16 saatlik sprint görev takvimi
├── PROJECT_STRUCTURE.md     # Dosya hiyerarşisi kılavuzu
├── requirements.txt         # Python bağımlılık listesi
├── app.py                   # Ana Streamlit arayüz ve görselleştirme uygulaması
└── utils/
    ├── __init__.py
    ├── data_fetcher.py      # NASA API veri çekme ve işleme modülü
    └── analyzer.py          # Trend analizi ve istatistiksel hesaplama modülü