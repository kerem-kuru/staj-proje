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
- Ek-16'yı PDF olarak yükler ve denetim sonucunu hemen görür.
- Formdan okunan bilgileri ve bulunan her hatayı/uyarıyı ayrı ayrı inceler.
- "Hatalı/Eksik" çıkan formu düzeltip yeniden yükler; önceki denetim raporları saklanır.

**Yönetici (staj komisyonu)**
- Öğrenci listesini CSV olarak içe aktarır.
- Tüm belgeleri statüye göre listeler, raporlarını ve geçmişini inceler.
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
| Zorunlu alanların dolu olması | 'Staj yeri adı' alanı boş bırakılmış. |
| Değerlerin biçimi (tarih, E/H, sayı) | 'Staj başlama tarihi' alanındaki '32.13.2027' değeri anlaşılamadı; GG.AA.YYYY biçiminde yazılmalı. |
| Öğrenci listesiyle eşleşme (numara, ad soyad, T.C. no, bölüm) | Belgedeki öğrenci numarası sizin numaranızla uyuşmuyor. |
| T.C. kimlik numarası algoritması (yabancı uyruk kabul edilir) | 'T.C. kimlik no / uyruğu' geçerli bir T.C. kimlik numarası değil. |
| E-posta ve telefon biçimi | 'Yetkili e-posta adresi' geçerli bir e-posta adresi değil. |
| Formun staj başlangıcından en az 30 gün önce teslimi | Stajın başlamasına 14 gün kaldı. |
| Staj gün sayısının tarihlerle uyuşması (hafta sonu ve resmî tatiller hesaba katılır) | Formda staj gün sayısı 25 yazıyor, ancak tarihler arasında 20 iş günü var. |
| Asgari staj süresi | Staj süresi en az 20 iş günü olmalı. |
| Sağlık yardım statüsünde tek seçim, 25 yaş notu | … 25 yaş ve üstü öğrenciler sağlık yardım statüsünde 6 numaralı seçeneği işaretler. (uyarı) |
| Yurtdışı / ücretli staj yükümlülükleri | Ücretli stajda staj bitiminde EK-18 … dekontla birlikte komisyona teslim edilmelidir. (uyarı) |
| Öğrenci imzası, işveren kaşe ve imzası | Belgede firma kaşesi ve yetkili imzası bulunamadı. |

Hatalar formun onaylanmasını engeller. Uyarılar ise yalnızca bilgilendirme amaçlıdır.

**Okunabilen belgeler:** Bilgisayarda doldurulup PDF olarak kaydedilmiş Ek-16. Taranmış belge,
fotoğraf ve JPG/PNG dosyalarında okunacak metin olmadığından bunlar şu an desteklenmiyor. Böyle bir
belge yüklenirse nedeni rapor edilir.

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
- **Kalıtım:** `BaseValidator → FieldFormatValidator → NationalIdValidator / EmailFormatValidator / PhoneFormatValidator`
  hiyerarşisi kuruldu. Ayrıca `RolePermission → IsStudent / IsAdmin`.
- **Çok biçimlilik:** `ValidationEngine` tüm kuralları aynı `validate()` çağrısıyla çalıştırır. Öğrenci
  ve yönetici politikaları aynı arayüzü farklı kurallarla uygular.
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

Denemek için `backend/readers/tests/fixtures/` klasöründeki dosyaları kullanabilirsiniz:
- `ek16_bos.pdf`: boş form, **Hatalı/Eksik** olur.
- `ek16_dolu.pdf`: demo öğrenci için doldurulmuş form, **Onaylandı** olur.

### Testler

```bash
cd backend && pytest
cd frontend && npm run lint && npm run build
```

## API

Tüm yanıtlar JSON biçimindedir. Hatalar her zaman `{"detail": "...", "errors": {alan: [mesajlar]} | null}` biçiminde döner.

| Metot | Yol | Kim | Açıklama |
|-------|-----|-----|----------|
| POST | `/api/auth/login/` | herkes | `{email, password}` → `{access, refresh}` |
| POST | `/api/auth/refresh/` | herkes | erişim token'ını yeniler |
| POST | `/api/auth/register/` | herkes | öğrenci kaydı (numara öğrenci listesinde olmalı) |
| GET | `/api/auth/me/` | giriş yapmış | oturumdaki kullanıcı |
| GET | `/api/documents/?status=` | öğrenci: kendi, yönetici: tümü | belge listesi |
| POST | `/api/documents/` | öğrenci | Ek-16 yükle (multipart `file`) |
| GET | `/api/documents/{id}/` | sahibi / yönetici | detay, okunan bilgiler, rapor geçmişi |
| POST | `/api/documents/{id}/reupload/` | öğrenci | Hatalı/Eksik belgeyi yeniden yükle |
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
docs/                diyagramlar ve rapor notları
```
