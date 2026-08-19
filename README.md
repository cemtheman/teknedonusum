# Sessiz Akım — Elektrikli Tekne Dönüşüm Simülatörü

## Projenin amacı

Sessiz Akım; elektrikli yolcu teknesi dönüşüm/satın alma alternatiflerini ve filo senaryolarını değerlendirmek için geliştirilmiş bir **ön karar-destek simülatörüdür**. Köyceğiz–Dalyan operasyon bağlamında teknik, enerji, yatırım ve işletme sonuçlarını karşılaştırmalı olarak sunar.

Bu uygulama nihai tekne tasarım yazılımı, klas onaylı mühendislik yazılımı veya CFD aracı değildir. Gemi inşaatı ve gemi makineleri hesaplarının, gerçek tekne geometrisinin, deniz tecrübelerinin ya da klas ve yetkili idare onaylarının yerine geçmez.

## Mevcut yetenekler

- v1, v2 ve v3 tekne alternatiflerinin teknik ve ekonomik karşılaştırması
- Tekne adetlerine göre filo senaryosu hesabı
- Operasyon hızı, günlük rota mesafesi ve güneşlenme süresi girdileri
- Ön/kalibre sevk gücü ve günlük sevk enerjisi tahminleri
- Güneş enerjisi katkısı ve net dış/şebeke enerjisi ihtiyacı
- Yatırım maliyeti, hibe ve net yatırım karşılaştırması
- Dizel ve elektrikli işletme maliyeti karşılaştırması
- Basit geri ödeme süresi ve CO₂ azaltımı tahmini
- Yönetim odaklı tekne karar özeti
- Varsayımlar ve veri kaynakları şeffaflığı
- Karar özeti ve varsayımları içeren XLSX çıktısı

## Operasyon hızı ve Komisyon hız kriteri

**Operasyon/seyir hızı**, kullanıcının seçtiği senaryo hızıdır; güç, seyahat süresi ve enerji hesaplarında kullanılır.

**Teknik Komisyon hız kriteri** ise teknenin sağlaması gereken hız kabiliyetidir ve mevcut yapılandırmada 10 knottur. Operasyon hızıyla aynı kavram değildir. Doğrulanmış tasarım/azami hız kabiliyeti henüz modele eklenmediğinden tam teknik uygunluk v1, v2 ve v3 için **“Henüz değerlendirilmedi”** olarak gösterilir.

## Tekne modellerinin hesap derinliği

- **v1**, uygulanabildiği yerlerde ön teknik senaryoyu kullanır.
- **v2 ve v3**, mevcut kalibre ön tekne-fiziği tahminlerini kullanır.

Bu modeller aynı hesap derinliğine sahip değildir. Sonuçlar ön karar desteği içindir; doğrulanmış tekne performansı iddiası taşımaz.

## Islak yüzey alanı notu

v1 direnç normalizasyonunda kullanılan yapılandırılmış ıslak yüzey alanı **30,0 m²**'dir. Geometri makullük (sanity) kontrolü yaklaşık **27,45 m²** sonuç verir. Bu kontrol yalnızca bilgilendirme amaçlıdır; tahmini değer direnç temel değerindeki 30,0 m² yerine otomatik olarak kullanılmaz.

## Veri kaynakları

Uygulama aşağıdaki kaynak türlerini açıkça ayırır:

- Kullanıcı girdileri
- Teknik Komisyon kriterleri
- Ön mühendislik varsayımları
- Kalibre ön tahminler
- Hesaplanan sonuçlar
- Erişilebildiğinde canlı EUR/TRY kuru
- Erişilebildiğinde canlı dizel fiyatı

Canlı piyasa servislerine ulaşılamazsa uygulama tanımlı statik yedek değerlere döner ve bu durumu veri kaynağı etiketinde belirtir.

## Kurulum ve çalıştırma

Python sanal ortamını oluşturun:

```bash
python -m venv .venv
```

macOS/Linux üzerinde etkinleştirin:

```bash
source .venv/bin/activate
```

Windows PowerShell üzerinde etkinleştirin:

```powershell
.venv\Scripts\Activate.ps1
```

Bağımlılıkları kurup uygulamayı başlatın:

```bash
pip install -r requirements.txt
streamlit run app.py
```

`requirements.txt`, XLSX dışa aktarımı için `openpyxl` bağımlılığını içerir.

## Testler

Tam test paketini çalıştırmak için:

```bash
pytest
```

Commit 43 anındaki test görünümü **362 başarılı testtir**. Bu sayı geliştirme ilerledikçe değişebilecek bir anlık görüntüdür; kalıcı bir test sayısı garantisi değildir.

## Tipik kullanım akışı

1. Sidebar üzerinden filo adetlerini belirleyin.
2. Operasyon günleri, seyir hızı, günlük rota, güneşlenme ve piyasa girdilerini ayarlayın.
3. Filo dashboard sonuçlarını inceleyin.
4. Tekne Alternatifleri Karar Özeti'ni karşılaştırın.
5. Gerektiğinde kapalı varsayımlar/veri kaynakları ve teknik karşılaştırma bölümlerini açın.
6. Karar özetini XLSX olarak indirin.

## Model sınırlamaları

- Direnç ve güç değerleri ön/kalibre tahminlerdir.
- CFD analizi içermez.
- Nihai pervane boyutlandırması ve sevk sistemi eşleştirmesi yapmaz.
- Doğrulanmış azami hız kabiliyeti henüz mevcut değildir.
- Klas veya yetkili idare onayı sağlamaz.
- Proje olgunlaştıkça varsayımlar gerçek tekne geometrisi, deplasman, hidrostatik, tasarımcı/üretici ve seyir tecrübesi verileriyle değiştirilmelidir.

## Proje durumu

**MVP / preliminary decision-support stage**

Uygulama üretim sertifikasyonu veya doğrulanmış tekne performansı iddiasında bulunmaz.
