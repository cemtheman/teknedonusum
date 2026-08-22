# Sessiz Akım — Quiet Current

**Elektrikli tekne dönüşümü için teknik ve ekonomik ön değerlendirme platformu**

Sessiz Akım; özellikle Dalyan–Köyceğiz operasyon bağlamında mevcut tekne filosunun elektrikli ve ileride hibrit dönüşüm seçeneklerini teknik, enerji, yatırım ve finansman boyutlarıyla değerlendirmek için geliştirilen bir karar-destek platformudur.

Uygulama; tekne bazlı ön boyutlandırmayı, filo ölçeğindeki enerji ve yatırım analizini, Excel tabanlı gerçek envanter planlamasını ve ilk yıl hibe programı senaryosunu aynı hesap zincirinde birleştirir.

> Sessiz Akım bir nihai tekne tasarım, klas onay, CFD veya sertifikasyon yazılımı değildir. Sonuçlar ön teknik ve ekonomik değerlendirme niteliğindedir.

---

## Mevcut ürün seviyesi — v0.2

Ana hesap zinciri:

**Tekne tipi + hizmet hızı + günlük rota → kurulu mekanik güç → elektriksel tüketim → günlük rota enerjisi → nominal batarya → solar/kıyı enerji dengesi → yatırım ve işletme ekonomisi → filo analizi → ilk yıl hibe planlaması**

Excel envanter modülü:

**Excel tekne listesi → tekne bazlı dönüşüm fazı → Faz 1 aday havuzu → hedef Tip 1 / Tip 2 / Tip 3 dağılımı → aktif filo senaryosu → yatırım / hibe / özkaynak analizi**

---

## Temel yetenekler

### Teknik ön boyutlandırma

- 5–10 knot çalışma aralığında hizmet hızı senaryosu
- Günlük rota mesafesine dayalı operasyon modeli
- Normatif / piyasa referanslı kurulu mekanik güç yaklaşımı
- Mekanik güçten elektrik tüketimine geçiş
- Günlük rota enerjisi ve nominal batarya ihtiyacı
- V1 / V2 / V3 için ortak semantik hesap zinciri
- Tip 4A için Tip 1, Tip 4B için Tip 2 teknik profilinin kullanılması
- Teknik uygunluk ve karşılaştırma ekranları

### Sezon ve operasyon günü modeli

Takvimsel sezon ile fiili operasyon günü birbirinden ayrıdır:

- `season_days`: başlangıç ve bitiş tarihleri arasındaki takvim süresi
- `operating_days`: teknenin fiilen çalıştığı gün sayısı

PV üretimi sezonun tüm takvim günlerinde devam eder. Operasyonel tekne yükü yalnız fiili operasyon günlerinde oluşur. Varsayılan operasyon günü sayısı sezon süresine eşittir; kullanıcı daha düşük bir değer tanımlayabilir.

### Solar ve kıyı enerjisi

- PVGIS sezonluk solar kaynak entegrasyonu
- PVGIS saatlik tipik üretim profili
- Saatlik batarya, PV ve kıyı enerjisi dengesi
- PV'nin önce aktif elektrik yükünü karşılaması
- Kalan PV üretiminin bataryaya yönlendirilmesi
- Batarya rezerv sınırı sonrası kıyı enerjisi hesabı
- Sezon sonu SOC farkının normalize edilmesi
- Saatlik PVGIS servisi kullanılamadığında kontrollü fallback

### Piyasa ve lokasyon verileri

Uygulama erişilebildiğinde TCMB EUR/TRY kuru, Aytemiz Muğla/Ortaca dizel fiyatı ve lokasyon verilerini otomatik alır. Canlı kaynağa erişilemezse tanımlı yedek değerler kullanılır ve canlı/yedek veri ayrımı UI üzerinde gösterilir.

---

## Tekne ve filo profilleri

| Profil | Referans tekne | Kapasite | Hibe senaryosu |
| --- | --- | ---: | ---: |
| Tip 1 | 12 m tek gövdeli | 24 kişi | Kooperatif %55 |
| Tip 2 | 13,5 m katamaran | 32 kişi | Kooperatif %55 |
| Tip 3 | 14 m katamaran | 54 kişi | Kooperatif %70 |
| Tip 4A | Tip 1 teknik profili | 24 kişi | Kooperatif dışı %40 |
| Tip 4B | Tip 2 teknik profili | 32 kişi | Kooperatif dışı %40 |

Tip 4 profilleri bağımsız yeni gövde modelleri değildir; finansman statüsünü ayırmak amacıyla Tip 1 / Tip 2 teknik zincirlerini kullanırlar.

---

## Excel filo envanteri analizi

Sidebar'daki **Filo Envanteri & Dönüşüm Planı** modülü `.xlsx` tekne listesini analiz eder.

Beklenen temel sütunlar:

- Tekne Adı
- Donatanı
- Tekne Cinsi
- Boyu (m)
- Eni (m)

Başlık satırının üstünde açıklama veya not satırları bulunabilir; parser gerçek başlık satırını otomatik arar.

### Dönüşüm fazları

- **Yolcu Motoru → Faz 1:** doğrudan elektrikli dönüşüm adayı
- **Ticari Yat / Gezinti-Tenezzüh Gemisi → Faz 2:** hibrit / jeneratör destekli elektrik için koşullu değerlendirme
- **Özel Tekne → Faz 3:** elektrikli / hibrit, malik kararı
- diğer tekne türleri → **Özel İnceleme**

Faz 2 ve Faz 3 teknik/finansal metodolojisi kurul kararı oluşana kadar bilinçli olarak dondurulmuştur. Uygulama bu gruplar için maliyet, hibe veya batarya/jeneratör büyüklüğü varsaymaz.

### Faz 1 hedef filo dağılımı

Excel'deki Yolcu Motorları mevcut gövde ölçülerine göre doğrudan V1/V2/V3'e zorla eşlenmez. Önce Faz 1 aday havuzu oluşturulur, ardından hedef filo politikası uygulanır.

Varsayılan hedef dağılım:

- Tip 1: %50
- Tip 2: %30
- Tip 3: %20

Kullanıcı oranları sidebar üzerinden değiştirebilir. Adet dağılımında toplam tekne sayısını koruyan largest-remainder yöntemi kullanılır.

Excel yüklenmesi manuel filo senaryosunu otomatik değiştirmez. **Envanter planını aktif senaryo olarak kullan** seçeneği işaretlenirse envanterden üretilen Tip 1/2/3 adetleri aktif hesap zincirine geçer.

---

## Envanter Dönüşüm Analizi ekranı

Excel yüklendiğinde ana ekranda ayrı bir analiz bölümü oluşur. Başlıca çıktılar:

- toplam envanter ve faz dağılımı
- Faz 1 hedef Tip 1 / Tip 2 / Tip 3 dağılımı
- Faz 1 toplam hedef yatırım
- toplam hibe ve özkaynak ihtiyacı
- ilk yıl desteklenebilecek tekne sayısı
- ilk yıl tahsis edilebilen hibe
- ilk yıl harekete geçen yatırım
- ilk yıl sonrası kalan Faz 1 tekne sayısı
- tekne bazlı karar ve gerekçe tablosu

---

## Hibe programı

İlk yıl için dört kaynak varsayılan olarak tek bir birleşik senaryo havuzu şeklinde ele alınır:

| Kaynak | Varsayılan ilk yıl bütçesi |
| --- | ---: |
| Bakanlık | 200 milyon TL |
| GEKA | 0 TL |
| YİKOB | 100 milyon TL |
| Sıfır Atık Vakfı | 100 milyon TL |
| **Toplam** | **400 milyon TL** |

Bu, gerçek fonların hukuki veya operasyonel olarak tek havuz olduğu anlamına gelmez. Gerçek uygunluk, başvuru, eş-finansman ve harcama kuralları henüz fon kaynağı bazında ayrı modellenmemektedir.

### Tahsis davranışı

**Yüksek öncelikli grup tamamlanmadan daha düşük öncelikli gruba geçilmez.**

Aynı öncelik seviyesinde daha düşük tekne-başı hibe ihtiyacı önce gelir.

İki kavram ayrı tutulur:

- **Bütçe karşılama oranı:** toplam bütçenin toplam hibe ihtiyacına oranı
- **Fiili tahsis oranı:** bütçenin tam tekne hibelerine gerçekten bağlanabilen bölümü

Bir sonraki tekneyi tam finanse edemeyen küçük bütçe bakiyeleri fiili tahsis hesabına dahil edilmez.

---

## Faz 2 ve Faz 3 karar sınırı

Kurul tarafından henüz teknik/finansal politika kararı alınmadığından:

### Faz 2

- hibrit / jeneratör destekli dönüşüm adayı olarak sınıflandırılır
- yatırım maliyeti ve batarya/jeneratör büyüklüğü hesaplanmaz
- hibe oranı varsayılmaz
- Faz 1 hibe bütçesine otomatik dahil edilmez

### Faz 3

- elektrikli / hibrit malik kararı olarak sınıflandırılır
- varsayımsal kamu hibesi üretilmez
- tekne-başı yatırım tutarı hesaplanmaz

Bu sınır bilinçlidir; kurul kararı oluşmadan model yeni politika varsayımı üretmez.

---

## Varsayılan senaryo

- Lokasyon: **Dalyan, Muğla**
- Günlük rota: **20 deniz mili**
- Operasyon hızı: yapılandırılmış varsayılan hizmet hızı
- Sezon: kullanıcı tarafından başlangıç/bitiş tarihiyle belirlenir
- Operasyon günü: sezon süresine eşit başlar, kullanıcı tarafından azaltılabilir
- Solar kaynak: PVGIS
- Filo envanteri: isteğe bağlı Excel yükleme

---

## Kullanıcı arayüzü

Uygulama Streamlit tabanlıdır.

Sol panelde:

- Filo Dönüşüm Hedefleri
- Filo Envanteri & Dönüşüm Planı
- Operasyon Profili
- Anahtar Teslim Piyasa Bedelleri
- Piyasa & Enerji Fiyatları
- Lokasyon, Sezon & Solar Kaynak
- Hibe Programı Bütçeleri

yer alır. Expander'lar varsayılan olarak kapalı başlar.

Ana ekranda senaryo/lokasyon özeti, envanter dönüşüm analizi, filo kompozisyonu, filo finansman özeti, solar/kıyı enerji dengesi, ilk yıl hibe programı, teknik ön boyutlandırma ve tekne bazlı finansal analizler sunulur.

---

## Kurulum

### Gereksinimler

- Python
- `pip`
- canlı piyasa, lokasyon ve PVGIS verileri için internet bağlantısı

Sanal ortam:

```bash
python -m venv .venv
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Bağımlılıklar:

```bash
pip install -r requirements.txt
```

Uygulamayı başlatın:

```bash
streamlit run app.py
```

---

## Testler

Tam test paketi:

```bash
pytest -q
```

Kod tabanı teknik hesap, enerji muhasebesi, hibe tahsisi, UI sözleşmeleri, fallback davranışları ve Excel envanteri için regresyon testleri içerir. README sabit test sayısı belirtmez; test sayısı ürün geliştikçe değişebilir.

---

## Repository hijyeni

Python bytecode/cache ve macOS metadata dosyaları repository dışında tutulur:

```text
__pycache__/
*.py[cod]
*$py.class
.DS_Store
```

---

## Model sınırları

Sessiz Akım'ın çıktıları **ön teknik ve ekonomik değerlendirme** niteliğindedir.

Mevcut model:

- CFD analizi yapmaz
- nihai gövde/hidrostatik tasarım yapmaz
- pervane ve sevk hattını klas seviyesinde boyutlandırmaz
- gerçek tekne ağırlık merkezi/stabilite hesabı yapmaz
- üretici performans garantisi vermez
- klas veya yetkili idare onayı sağlamaz
- Faz 2 hibrit sistemini henüz boyutlandırmaz
- Faz 3 özel tekne yatırımını henüz hesaplamaz
- Excel'de bulunmayan kooperatif üyeliği, yolcu kapasitesi veya motor gücü gibi bilgileri kendiliğinden tahmin etmez

Gerçek uygulama öncesinde tekne bazlı mevcut motor gücü, gerçek deplasman, yolcu kapasitesi, gövde/hidrostatik bilgiler, görev çevrimi, liman/şarj altyapısı, üretici verileri ile klas ve idare gereklilikleri doğrulanmalıdır.

---

## Proje durumu

**Sessiz Akım v0.2 — aktif geliştirme / karar-destek platformu**

v0.1 MVP baseline korunmaktadır. v0.2 ile ürün teknik ön boyutlandırma simülatöründen filo, envanter ve finansman planlama platformuna doğru genişlemiştir.

Mevcut odak:

- metodolojik hardening
- kullanıcı arayüzü sadeleştirmesi
- gerçek filo envanterine dayalı planlama
- Faz 1 hibe programının şeffaflaştırılması
- kurul kararı oluştuğunda Faz 2 / Faz 3 metodolojisinin kontrollü genişletilmesi

---

## Marka

**Sessiz Akım / Quiet Current**

**Daha sessiz. Daha temiz. Daha sürdürülebilir.**
