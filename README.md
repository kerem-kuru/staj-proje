# Staj Belge Denetimi (Ek-16)

Mühendislik öğrencilerinin staj başvurusunda teslim ettiği **Ek-16 Staj Kabul Formu**'nu otomatik
denetleyen bir web uygulaması.

Staj kabul formları bugün çoğunlukla elden teslim ediliyor ve staj komisyonu her formu tek tek
kontrol ediyor. Boş bırakılan alanlar, yanlış hesaplanan gün sayıları, eksik kaşe ya da geç teslim
gibi hatalar ancak bu aşamada fark ediliyor ve form öğrenciye geri dönüyor. Bu uygulamada öğrenci
formunu sisteme yüklüyor. Sistem formdaki bilgileri okuyup kurallara göre denetliyor ve eksikleri
anında, Türkçe ve madde madde raporluyor. Öğrenci hatalı formu düzeltip yeniden yüklüyor. Kurallardan
geçen form komisyonun onayına düşüyor.

Sistem yalnızca Ek-16 işler: farklı bir belge yüklenirse reddedilir.

## Ne yapıyor?

**Öğrenci**
- Okulun öğrenci listesinde kayıtlı numarasıyla hesap açar.
- Staj yapacağı haftalık günleri ve tarih aralığını seçip Ek-16'yı yükler, denetim sonucunu hemen görür.
- Formdan okunan bilgileri ve bulunan her hatayı/uyarıyı ayrı ayrı inceler.
- "Hatalı/Eksik" çıkan formu düzeltip yeniden yükler; önceki denetim raporları saklanır.

**Yönetici (staj komisyonu)**
- Öğrenci veri setini CSV olarak içe aktarır.
- Başvuruları statüye göre listeler, raporlarını ve geçmişini inceler; tamamlananlar ayrı sekmededir.
- Onaylanan belgeyi "Tamamlandı" olarak işaretler ya da gerekçe yazarak geri çevirir.
- Tamamlanan belgeler Ek-17 üretimine temel oluşturur.

## Belge statüleri

```
Yüklendi → İnceleniyor → Onaylandı → Tamamlandı
                       ↘ Hatalı/Eksik → (düzeltilip yeniden yüklenir) → Yüklendi …
```

- Denetim yükleme anında çalışır: hata yoksa **Onaylandı**, varsa **Hatalı/Eksik**.
- **Tamamlandı** statüsündeki belgeyi öğrenci değiştiremez ve silemez. Yalnızca yönetici güncelleyip silebilir.

## Neleri denetliyor?

Form, Kocaeli Üniversitesi Mühendislik Fakültesi Staj Kabul Formu (Ek-16) şablonuna göre okunur.

| Kural | Örnek bulgu |
|-------|-------------|
| Zorunlu alanların dolu olması (faks ve web adresi hariç) | 'Staj yeri adı' alanı boş bırakılmış. |
| Değerlerin biçimi (tarih, E/H, sayı) | 'Staj başlama tarihi' alanındaki '32.13.2027' değeri anlaşılamadı; GG.AA.YYYY biçiminde yazılmalı. |
| Veri setindeki kayıtla eşleşme (numara, ad soyad, kimlik no, uyruk, doğum tarihi, adres, önceki staj günü, e-posta, telefon, sağlık statüsü, bölüm) | Belgedeki 'Doğum tarihi' öğrenci kaydıyla uyuşmuyor. |
| Uyruğa göre kimlik kontrolü: T.C. için algoritma, yabancı uyruk için 11 hane ve 99 ile başlama | Yabancı uyruklu öğrencinin kimlik numarası 11 haneli olmalı ve 99 ile başlamalı. |
| E-posta biçimi | 'Yetkili e-posta adresi' geçerli bir e-posta adresi değil. |
| Telefon biçimi: `+90 xxx xxx xx xx` | 'Öğrenci telefon no' +90 xxx xxx xx xx biçiminde olmalı. |
| Adres: Mahalle, Cadde/Sokak, Bina No, Daire No, İlçe/İl sırası (staj yeri adresinde uyarı) | 'İkametgâh adresi' Mahalle, Cadde/Sokak, Bina No, Daire No, İlçe/İl sırasıyla ve tam yazılmalı … |
| Öğretim yılı: yarıyıl bilgisi, ardışık yıllar, teslim yılı ve staj tarihleriyle uyum | Öğretim yılındaki yıllar ardışık olmalı (ör. 2026-2027). |
| Formun staj başlangıcından en az 30 gün önce teslimi, önerilen tarih | … Önerilen teslim tarihi en geç 17.04.2027; bugün teslim için staj en erken 02.06.2027 tarihinde başlamalı. |
| Seçilen plandan hesaplanan günlerin (resmî tatiller çıkarılır) belgeyle uyuşması | Formda staj gün sayısı 25 yazıyor, ancak seçtiğiniz plana göre 20 iş günü var. |
| Asgari staj süresi | Staj süresi en az 20 iş günü olmalı. |
| Mühendis sayısı en az 1; 5'in altındaysa mezun olunan bölüm sorulur | Mühendis sayısı 5'in altında; mühendisin mezun olduğu bölümü belirtin. (uyarı) |
| Sağlık yardım statüsünde tek seçim, 25 yaş notu | … 25 yaş ve üstü öğrenciler sağlık yardım statüsünde 6 numaralı seçeneği işaretler. (uyarı) |
| Yurtdışı / ücretli staj yükümlülükleri | Ücretli stajda staj bitiminde EK-18 … dekontla birlikte komisyona teslim edilmelidir. (uyarı) |
| İşveren kısmı kaşe ve imzalı; öğrenci ve danışman onay kısımları boş | Öğrenci onay kısmı boş bırakılmalı. |

Hatalar formun onaylanmasını engeller. Uyarılar ise yalnızca bilgilendirme amaçlıdır.

**Okunabilen belgeler:** Word, PDF, JPEG ve PNG yüklenebilir; diğer türler reddedilir. İçeriği şu an
yalnızca bilgisayarda doldurulup PDF olarak kaydedilmiş Ek-16 okunabiliyor. Word, taranmış belge ve
fotoğraflar OCR entegrasyonuyla (final aşaması) okunacak; bunlar yüklenirse nedeni rapor edilir.

## Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python, Django 6.1, Django REST Framework, JWT (simplejwt) |
| PDF okuma | pdfplumber (formun tablo hücreleri üzerinden) |
| Frontend | React 19, Vite, React Router, axios |
| Veritabanı | Geliştirmede SQLite, üretimde PostgreSQL |
| Test | pytest, pytest-django |

## Nesne yönelimli tasarım

Proje, nesne yönelimli programlamanın dört ilkesini kodda açıkça gösterecek şekilde kurgulandı:

- **Soyutlama:** `DocumentReader` belgenin nasıl okunduğunu gizler. `BaseValidator` her kuralın iç
  mantığını gizler. `DocumentPolicy` rol bazlı erişimi gizler.
- **Kalıtım:** `BaseValidator → FieldFormatValidator → TurkishIdValidator / ForeignIdValidator / EmailFormatValidator /
  PhoneFormatValidator / AddressFormatValidator` hiyerarşisi kuruldu. Ayrıca `RolePermission → IsStudent / IsAdmin`.
- **Çok biçimlilik:** `ValidationEngine` tüm kuralları aynı `validate()` çağrısıyla çalıştırır.
  `NationalIdValidator` uyruğa göre T.C. ya da yabancı kimlik kuralını çalıştırır. Öğrenci ve yönetici
  politikaları aynı arayüzü farklı kurallarla uygular.
- **Kapsülleme:** Belgenin statüsü yalnızca izin verilen geçişlerle değişir; model kuralı atlayan
  değişikliği reddeder. Denetim sonucundaki bulgu listesi dışarıdan değiştirilemez.

Ayrıntılı eşleştirme `docs/rapor-notlari.md` içinde, sınıf ve akış diyagramları ise `docs/diyagramlar.md`
içinde yer alıyor.

## Kurulum

Gereksinimler: Python 3.12+, Node.js 20+.

### Backend

```bash
cd backend
python -m venv .venv              # Windows: py -m venv .venv
.venv\Scripts\activate            # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env              # DJANGO_SECRET_KEY değerini doldurun
python manage.py migrate
python manage.py seed_demo        # örnek öğrenci listesi + demo hesaplar (yalnızca geliştirme)
python manage.py runserver
```

### Frontend

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

### Demo hesapları

| Rol | E-posta | Şifre |
|-----|---------|-------|
| Yönetici | admin@staj.local | Admin.12345 |
| Öğrenci | ayse@ogrenci.edu.tr | Ogrenci.12345 |

Denemek için `deneme-verisi/` klasöründe veri seti ve her kural için ayrı Ek-16 senaryoları var;
adımlar ve beklenen sonuçlar `deneme-verisi/README.md` içinde.

### Testler

```bash
cd backend && pytest
cd frontend && npm run lint && npm run build
```

## API

Tüm yanıtlar JSON biçimindedir. Hatalar her zaman `{"detail": "...", "errors": {alan: [mesajlar]} | null}` biçiminde döner.

| Metot | Yol | Kim | Açıklama |
|-------|-----|-----|----------|
| POST | `/api/auth/login/` | herkes | `{email, password}` → `{access, refresh}`; 5 hatalı denemede 15 dakika kilit (423) |
| POST | `/api/auth/logout/` | giriş yapmış | kullanıcının tüm token'larını geçersiz kılar |
| POST | `/api/auth/refresh/` | herkes | erişim token'ını yeniler |
| POST | `/api/auth/register/` | herkes | öğrenci kaydı (numara öğrenci listesinde olmalı) |
| GET | `/api/auth/me/` | giriş yapmış | oturumdaki kullanıcı |
| GET | `/api/documents/?status=&exclude_status=` | öğrenci: kendi, yönetici: tümü | belge listesi |
| POST | `/api/documents/` | öğrenci | Ek-16 yükle (multipart `file`, `plan_start`, `plan_end`, `plan_weekdays`) |
| GET | `/api/documents/{id}/` | sahibi / yönetici | detay, okunan bilgiler, rapor geçmişi |
| POST | `/api/documents/{id}/reupload/` | öğrenci | Hatalı/Eksik belgeyi plan bilgisiyle yeniden yükle |
| POST | `/api/documents/{id}/engineer-department/` | öğrenci | `{engineer_department}` mühendisin mezun olduğu bölüm |
| GET | `/api/documents/{id}/download/` | sahibi / yönetici | dosyayı indir |
| DELETE | `/api/documents/{id}/` | sahibi (Tamamlandı değilse) / yönetici | sil |
| PATCH | `/api/documents/{id}/` | yönetici | `{admin_note}` |
| POST | `/api/documents/{id}/complete/` | yönetici | Onaylandı → Tamamlandı |
| POST | `/api/documents/{id}/reject/` | yönetici | `{note}` ile geri çevir |
| GET | `/api/students/?q=` | yönetici | öğrenci listesi |
| POST | `/api/students/import/` | yönetici | CSV içe aktar |
| GET | `/api/students/me/` | öğrenci | kendi profili |

## Klasör yapısı

```
backend/
  config/            ayarlar, URL'ler, JSON hata biçimi
  accounts/          kullanıcı, roller (ROLE_STUDENT, ROLE_ADMIN), izin sınıfları
  students/          öğrenci profili, CSV içe aktarma
  documents/         belge modeli, statü akışı, erişim politikaları, servisler, staj günü hesabı
  validation/        denetim kuralları, denetim motoru, rapor
  readers/           belge okuyucular (PDF form okuyucu)
  internship_forms/  staj formu entegrasyonu altyapısı
  exports/           Ek-17 üretim altyapısı
frontend/src/
  api/               axios istemcisi, token yenileme
  auth/              oturum yönetimi, korumalı sayfalar
  pages/student/     öğrenci sayfaları
  pages/admin/       yönetici sayfaları
  components/        ortak bileşenler
docs/                diyagramlar, PNG çıktıları, referans rapor ve rapor notları
deneme-verisi/       elle deneme için veri seti ve Ek-16 senaryoları
```
