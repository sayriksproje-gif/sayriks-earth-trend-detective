# Yükleme ve Link Rehberi (NASA Space Apps 2026)

Bu projede Space Apps Project sayfasına **dosya yüklemesi yapılmaz**. Demo, nihai proje ve kanıtlar **dış platformlara** yüklenir ve **herkese açık (public) link** olarak paylaşılır.

## 1) Nereye ne yüklenecek?

### A. Final Project (nihai proje) linki — önerilen: GitHub
- **Nereye:** [GitHub](https://github.com) üzerinde **Public repository**
- **Ne yüklenecek:**
  - Kaynak kod (`app.py`, `utils/`, `database/`, `.streamlit/` vb.)
  - `README.md` (proje özeti, kurulum/çalıştırma, kullanılan NASA/diğer veriler, demo ve final linkleri, SI notu)
  - `requirements.txt`, lisans, dokümantasyon
  - Rapor/sunum çıktıları (`RAPOR_Earth_Trend_Detective.html`), ekran görüntüleri, örnek CSV çıktıları
- **Yüklenmeyecek:** `.env`, şifreler, API anahtarları, kişisel/gizli veriler
- **Paylaşım:** Repo URL’si (örn. `https://github.com/<kullanici>/<repo>`) → Space Apps formunda **Link to Final Project**

**Örnek adımlar:**
1. GitHub’da yeni public repo oluşturun.
2. Yerelde remote ekleyip push edin:
   - `git remote add origin https://github.com/<kullanici>/<repo>.git`
   - `git add .` ( `.env` ve sırların hariç olduğundan emin olun)
   - `git commit -m "NASA Space Apps 2026 submission"`
   - `git push -u origin main` (veya aktif dal)

### B. Project Demo linki — 30 sn video veya ≤7 slayt
- **Video (≤30 sn) için nereye:** [YouTube](https://youtube.com) (Unlisted/Public) veya [Google Drive](https://drive.google.com) / OneDrive
  - Ekran kaydı önerisi: Kontrol paneli → Harita & Genel Bakış → Trend & İstatistik → Karşılaştırma & Kanıt → Sunum/Rapor
  - İngilizce anlatım veya **İngilizce altyazı zorunlu**
  - Erişim: “Herkese açık” / “Bağlantıya sahip herkes görüntüleyebilir”, şifre/izin yok
- **Slayt (başlık+giriş dahil ≤7 slayt) için nereye:** Google Slides / Canva / PowerPoint Online ya da PDF olarak Drive/GitHub
  - İngilizce, okunabilir ve görsel ağırlıklı
- **Paylaşım:** Public link → **Link to Project Demo**

### C. Yedek kanıt (önerilir)
- **Nereye:** Google Drive klasörü (public) ve/veya GitHub repo
- **Ne yüklenecek:** Ekran görüntüleri, tam ekran kaydı, `RAPOR_Earth_Trend_Detective.html`, örnek CSV’ler
- **Amaç:** Canlı demo sırasında internet/API/DB hatası olursa jüriye kanıt göstermek

## 2) Gönderim öncesi kontrol listesi
- [ ] Tüm linkler **gizli pencerede** açılıyor (şifre/izin/giriş istemiyor)
- [ ] Demo: ≤30 sn video veya ≤7 slayt; dil kuralları uygun
- [ ] Final project: kod/veri yöntemi/çalıştırma ve kanıtlar erişilebilir
- [ ] Project sayfası alanları İngilizce ve eksiksiz (NASA Data, SI, referanslar dahil)
- [ ] 18 yaş altı görsel/ses/benzerliği yok; SI kullanımı doğru beyan edildi
- [ ] Son gönderim: **15 Kasım 2026 23:59** (Local Event / Team Owner yerel saati), **Submit for Judging** tıklandı

## 3) Bu projede hazır/üretilmesi gereken çıktılar
- **Hazır:** `app.py`, analiz/görselleştirme, `RAPOR_Earth_Trend_Detective.html`, `SUNUM.md`, veritabanı şeması ve ingest scriptleri
- **Üretilmeli:** 30 sn demo videosu (veya 7 slayt), ekran görüntüleri/ekran kaydı yedeği, public GitHub repo, Space Apps portal metinleri/linkleri
- **Doğru adlandırma:** Çalışan prototip/Canlı demo (gerçek NASA POWER/MySQL verisi), Simülasyon/fallback modu (akış testi, bilimsel gözlem değil), Test/kanıt çıktısı (önceden üretilmiş rapor/kayıtlar)
