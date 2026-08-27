# Sessiz Akım — Kalıcı Proje Bağlamı

Bu belge yeni oturumlarda ve her yeni değişiklik öncesinde okunacak teknik
başlangıç noktasıdır. Sohbet hafızasının yerine geçmez; repository geçmişi,
mevcut kaynak kod ve testlerle birlikte doğrulanır.

## 1. Güvenilir işlevsel baseline

- Doğrulanan işlevsel commit: `47740a396c69004ff066f10958603d3340529f80`
- Commit mesajı: `feat: add phase 1 journey demand dashboard`
- Yerel regresyon: `1112 passed`
- GitHub Actions: yeşil
- Görsel kontrol: başarılı
- `main` ve `origin/main`: senkron
- Çalışma ağacı: temiz
- Doğrulama tarihi: 27 Ağustos 2026

Bu belgeyi ekleyen dokümantasyon commitinin ebeveyni yukarıdaki işlevsel
baseline'dır. Sonraki işlevsel checkpointlerde bu bölüm güncellenmelidir.

## 2. Ürün ve metodoloji sınırı

Sessiz Akım, nihai tasarım veya sertifikasyon yazılımı değil; elektrikli tekne
dönüşümü için teknik ve ekonomik ön değerlendirme platformudur.

v0.2 ana teknik zinciri:

`Tekne tipi + hizmet hızı + günlük rota → kurulu mekanik güç → elektriksel
tüketim → günlük rota enerjisi → nominal batarya → solar/kıyı enerji dengesi →
yatırım ve işletme ekonomisi → filo analizi → ilk yıl hibe planlaması`

Temel kararlar:

- Aktif teknik ve finansal geliştirme odağı Faz 1 yolcu motorlarıdır.
- Faz 2 hibrit ve Faz 3 özel tekne metodolojisi kurul kararı oluşana kadar
  dondurulmuştur.
- V1/V2/V3 aynı semantik hesap zincirinden geçer.
- Tip 4A, Tip 1; Tip 4B, Tip 2 teknik profilini kullanır. Tip 4 profilleri yeni
  gövde modelleri değildir; finansman statüsünü ayırır.
- Excel envanteri manuel senaryoyu kendiliğinden değiştirmez. Yalnız kullanıcı
  envanter planını aktif senaryo yaptığında ana hesap zincirine geçer.
- Envanterde teknik anahtar `vessel_id`, kullanıcıya görünen benzersiz kimlik
  `plate_number` alanıdır. Ticari seri `T-001…T-360`, özel seri
  `Ö-001…Ö-132` biçimindedir.
- Excel'de bulunmayan yolcu kapasitesi, motor gücü, kooperatif statüsü veya
  başka saha verileri tahmin edilmez.

## 3. Yolculuk talebi katmanı

Tamamlanan zincir:

`JourneyDemandPeriod → katı Excel içe aktarma → rota bazlı karar üretmeyen özet
→ Streamlit yükleme ve gösterim`

İlgili checkpointler:

- `113aa30`: Faz 1 yolculuk talebi veri sözleşmesi
- `69b2f9c`: mockup yolculuk talebi Excel içe aktarıcısı
- `44ea804`: rota bazlı yolculuk talebi özeti
- `47740a3`: yükleme ve analiz arayüzü

Kilitli davranışlar:

- Sezon 1 Nisan–30 Eylül'dür.
- Excel yalnız `Mockup Yolculuk Talebi` sayfasını ve tanımlı 14 sütunu katı
  biçimde okur.
- Gün sayısı, yolcu bacağı, günlük ortalama ve pik günlük talep modelde tekrar
  saklanmaz; ham girdilerden türetilir ve Excel değerleriyle uzlaştırılır.
- Dönem kimlikleri benzersizdir. Aynı rotadaki çakışan dönemler ve aynı rota
  kimliğine bağlı farklı rota adları reddedilir.
- Ziyaretçi sayıları yalnız kalibrasyon bağlamıdır; otomatik olarak tekne
  yolculuğuna dönüştürülmez.
- Bu katman sefer sayısı, tekne kapasitesi, filo/tekne ataması, enerji ihtiyacı,
  altyapı yeterliliği, gelir, yatırım sıralaması veya optimizasyon üretmez.

2025 mockup uzlaştırma değerleri:

- 6 dönem
- 183 hizmet günü
- 632.000 gidiş-dönüş yolcu
- 1.264.000 tek yön yolcu bacağı
- 3.453,55 günlük ortalama
- En yüksek dönem: Ağustos 2025
- Pik günlük talep: 8.355

Bu değerler sentetiktir ve saha doğrulaması gerektirir.

## 4. UI'de korunacak davranışlar

- Sağ ana frame'de ikinci bir marka başlığı bulunmaz.
- Marka alanı sidebar ve footer'da korunur.
- Masaüstü ana içerik üst boşluğu Streamlit araç çubuğuyla çakışmayacak şekilde
  korunur.
- `Senaryo ve Lokasyon Özeti` ile yolculuk talebi paneli uzak PVGIS çağrısından
  önce render edilir; PVGIS beklenirken ana panel boş kalmaz.
- Sidebar bölümleri varsayılan olarak kapalıdır.
- UI değişiklikleri kaynak testleriyle birlikte gerçek Streamlit görsel
  kontrolünden geçmeden tamamlanmış sayılmaz.

## 5. Değişiklik protokolü

Her yeni işte sıra şöyledir:

1. `HEAD`, çalışma ağacı, `main/origin/main` ve son test baseline'ını doğrula.
2. Bu belgeyi, ilgili dosyaları, testleri ve geçmiş commitleri oku.
3. Önceden alınmış ürün kararlarını ve kapsam dışı alanları açıkça koru.
4. En küçük bağımsız TDD dilimini belirle; tam dosya değişimini son çare yap.
5. Windows, VS Code ve PowerShell ortamına uygun komutlar ver;
   testleri `python -m pytest` ile çalıştır.
6. Odak testlerini ve tam regresyonu çalıştır; `git diff --check` uygula.
7. UI değişikliğinde gerçek görsel kontrol yap.
8. Yalnız beklenen dosyaları açıkça stage et; commit, push ve GitHub Actions
   sonucunu doğrula.

## 6. Açık konu ve sıradaki adım

Yolculuk talebi katmanı tamamlandı. Sıradaki teknik konu, bu doğrulanmış talebi
ayrı bir aşağı-akış hizmet kapasitesi katmanında ele almanın metodolojisini
kilitlemektir.

Kod yazmadan önce açıkça karara bağlanması gereken girdiler:

- rota bazlı hangi filo/tekne havuzunun hizmet verdiği,
- doğrulanmış kullanılabilir yolcu kapasitesi,
- doluluk/yük faktörünün veri dayanağı,
- tekne başına günlük gidiş-dönüş yapabilme sınırı,
- hizmet penceresi ve saha operasyon kısıtları.

Bu girdiler tanımlanmadan sefer sayısı, gerekli tekne adedi, kapasite yeterliliği
veya filo ataması hesaplanmayacaktır. İlk sonraki dilim kod değil, bu metodoloji
ve veri sözleşmesi kararının kilitlenmesidir.

## 7. Bilinçli olarak değiştirilmemesi gerekenler

- v0.1 MVP baseline ve mevcut v0.2 teknik hesap zinciri
- compliance eşikleri ve mevcut enerji/batarya hesap semantiği
- Faz 2/Faz 3 için kurul kararı olmadan maliyet, hibe veya sistem boyutlandırma
- ziyaretçi sayısından otomatik yolculuk/sefer türetme
- yolculuk talebi modeline tekne, enerji, gelir veya optimizasyon alanları ekleme
- ana frame marka başlığını geri getirme
