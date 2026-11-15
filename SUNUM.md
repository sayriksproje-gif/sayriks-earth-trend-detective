# Earth Trend Detective — Jüri Sunumu (7+ Sayfa)

**NASA Space Apps Challenge 2026 (Ankara, Solo & Sanal)**  
**Odak:** Etki • Yaratıcılık • Gerçekçilik • Geçerlilik • Sunum  
**Önerilen süre:** 3–4 dakika (Slayt 5 canlı demo: 45–60 sn)

---

## Slayt 1 — Başlık & Problem
**Odak:** Etki ve bağlam

### Ekranda gösterilecekler
- Proje adı: **Earth Trend Detective**
- Takım: Tek kişi / Sanal (Ankara)
- Tek cümlelik problem ve etki cümlesi

### Ana mesajlar
- İklim göstergelerindeki trend ve anomalileri hızlı, anlaşılır ve güvenilir şekilde izlemek zordur.
- Bu araç, NASA açık verilerini kullanarak seçili lokasyonlarda erken içgörü ve önceliklendirme desteği sağlar.

### Konuşma notu
"Merhaba, ben Earth Trend Detective projesini sunuyorum. Amaç; NASA açık verileriyle lokasyon bazlı trend ve anomalileri anlaşılır biçimde ortaya koyarak erken içgörü sağlamaktır."

### Demo geçişi
Ana sayfa başlığı ve etki cümlesini göster.

---

## Slayt 2 — Hedef Kullanıcı & Etki
**Odak:** Kimin işine yarar, hangi faydayı sağlar

### Ekranda gösterilecekler
- Hedef kullanıcı profilleri
- Örnek kullanım senaryosu
- Beklenen fayda

### Ana mesajlar
- Hedef kullanıcı: öğrenciler, yerel planlayıcılar, araştırmacılar ve iklim farkındalığı yüksek bireyler.
- Senaryo: Lokasyon ve dönem seçerek sıcaklık/nem gibi göstergelerde eğilim ve sapmaları incelemek.
- Fayda: Hızlı görünürlük, karşılaştırma ve veri temelli farkındalık (nihai karar yerine erken içgörü).

### Konuşma notu
"Kullanıcı, merak ettiği bölgeyi seçer ve döneme göre trend-anomali özetini görür. Böylece hangi bölgelerin daha dikkat çekici sinyal verdiğini hızlıca ayırt edebilir."

### Demo geçişi
Sidebar üzerinden lokasyon, parametre ve dönem seçimini göster.

---

## Slayt 3 — Veri Kaynakları (Gerçekçilik)
**Odak:** NASA/partner açık verilerin kullanımı ve şeffaflık

### Ekranda gösterilecekler
- Veri kaynağı modu (NASA POWER / Offline-Demo)
- Parametre listesi (örn. T2M, RH2M, PRECTOTCORR)
- Atıf ve uyum notları

### Ana mesajlar
- Birincil kaynak: **NASA POWER** günlük nokta zaman serisi verisi.
- Referans/doğrulama bağlamı: Giovanni, KNMI Climate Explorer vb. (kullanım durumuna göre).
- Veri kaynağı, parametre, birim ve dönem arayüzde açıkça gösterilir.
- Simülasyon modu yalnızca offline/demo amaçlıdır ve etiketlenir.
- **Non-endorsement:** Bu proje NASA tarafından onaylanmamaktadır; NASA açık verilerini kullanır.

### Konuşma notu
"Uygulamanın gerçekçi tarafı, NASA POWER üzerinden gerçek zaman serisi çekebilmesidir. Simülasyon yalnızca offline/demo amaçlı, etiketli fallback olarak bulunur."

### Demo geçişi
Veri kaynağı modu ve parametre seçimini göster.

---

## Slayt 4 — Yöntem & Geçerlilik
**Odak:** Analiz yöntemi, istatistiksel dayanak, sınırlılıklar

### Ekranda gösterilecekler
- Analiz akışı: veri alımı → temizleme → analiz → görselleştirme
- İstatistikler: eğim, R², p-value, anlamlılık yorumu

### Ana mesajlar
- Ön işleme: eksik/geçersiz değerlerin ayıklanması (örn. -999).
- Trend analizi: lineer regresyon ile eğim, R² ve p-value hesaplanır.
- Yorumlama: p-value ve örneklem büyüklüğüne göre anlamlılık değerlendirmesi yapılır.
- Varsayımlar ve sınırlılıklar (otokorelasyon, veri boşlukları, doğrusal model) şeffaf biçimde sunulur.

### Konuşma notu
"Sadece çizgi göstermek yerine, eğilimin güvenilirliğini p-value ve R² ile birlikte yorumluyoruz. Böylece geçerlilik kriterini destekliyoruz."

### Demo geçişi
Trend & İstatistik sekmesindeki metrikleri ve yorum rehberini göster.

---

## Slayt 5 — Canlı Demo & Bulgular
**Odak:** Çalışan ürün, somut çıktı, yaratıcılık

### Ekranda gösterilecekler
- Harita & Genel Bakış
- Günlük/yıllık trend ve anomali grafikleri
- Hızlı karşılaştırma tablosu / içgörü

### Ana mesajlar
- Akış: lokasyon seçimi → veri alımı → trend/anomali analizi → yorum.
- Bulgular: dönemsel eğilim (birim/10 yıl), anlamlılık yorumu, öne çıkan sapmalar.
- Yaratıcı katman: karşılaştırmalı trend taraması ve içgörü odaklı sunum.

### Konuşma notu
"Şimdi canlı olarak seçili lokasyon için veriyi çekiyor, trend ve anomaliyi gösteriyorum. Ardından karşılaştırma tablosuyla hangi lokasyonların daha güçlü sinyal verdiğini özetliyorum."

### Demo geçişi
Harita & Genel Bakış ve Trend & İstatistik sekmelerinde canlı gezin (45–60 sn).

---

## Slayt 6 — Yaratıcılık, Etki ve Sınırlılıklar
**Odak:** Fark yaratan değer ve dürüst değerlendirme

### Ekranda gösterilecekler
- İçgörü kartları / özet yorum
- Metodoloji & Kaynaklar sekmesinden sınırlılıklar

### Ana mesajlar
- Yaratıcılık: Trend + anomali + anlamlılık + içgörü/karşılaştırma yaklaşımı.
- Etki: Karmaşık zaman serisini hızlı ve yorumlanabilir içgörüye dönüştürme.
- Sınırlılıklar: tek nokta/parametre kapsamı, veri ürün farklılıkları, doğrusal varsayım; kritik kararlar için uzman değerlendirmesi gerekir.

### Konuşma notu
"Projeyi farklı kılan, veriyi sadece görselleştirmek değil; anlamlılık ve yorum katmanıyla karar destek içgörüsüne dönüştürmesidir. Sınırlılıkları da şeffaf biçimde paylaşıyoruz."

### Demo geçişi
İçgörü kutusu ve Metodoloji & Kaynaklar sekmesini göster.

---

## Slayt 7 — Sonuç, Yol Haritası & Kaynaklar
**Odak:** Kapanış, sürdürülebilirlik, atıf

### Ekranda gösterilecekler
- Sonuç özeti
- Yol haritası maddeleri
- Kaynak/atıf ve repo/demo linkleri

### Ana mesajlar
- Sonuç: Gerçek NASA verisiyle trend/anomali tespiti için çalışan, açık ve tekrarlanabilir bir prototip.
- Yol haritası: ek parametreler, gelişmiş testler (örn. Mann-Kendall), çoklu gösterge analizi, SWOT/RCM/hidroloji verileriyle genişleme.
- Kaynaklar: NASA POWER, NASA Space Apps Challenge ve ilgili kaynaklar (Giovanni, AppEEARS, CDO, KNMI vb. - kullanım durumuna göre).

### Konuşma notu
"Özetle Earth Trend Detective, gerçek veri ve geçerli analizle erken içgörü sunar. Sonraki adımda kapsamı genişleterek daha güçlü bir karar destek aracına dönüştürülebilir. Teşekkür ederim."

### Demo geçişi
Metodoloji & Kaynaklar ve repo/demo bağlantılarını göster.

---

## (Opsiyonel) Slayt 8 — Teknik Mimari & Soru-Cevap (Yedek)
- Mimari: `app.py` (UI) + `utils/data_fetcher.py` (NASA POWER) + `utils/analyzer.py` (istatistik/trend)
- Çalıştırma: `streamlit run app.py`
- Yedek notlar: veri boşluğu, API hatası yönetimi, simülasyon fallback etiketi

---

## Sunum Kontrol Listesi
- [ ] Gerçek NASA verisi ile en az bir canlı örnek gösterildi
- [ ] Eğilimle birlikte p-value/R² ve yorum verildi
- [ ] Etki cümlesi ve hedef kullanıcı net ifade edildi
- [ ] Veri atıfı ve NASA non-endorsement notu paylaşıldı
- [ ] Sınırlılıklar ve yol haritası belirtildi
- [ ] Süre 3–4 dakika içinde, akıcı geçişlerle tamamlandı
