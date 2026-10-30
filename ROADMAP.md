# Yol Haritası

## Aşama 1 — Ara teslim (iskelet + çalışan akış) ✅

- [x] Django + DRF projesi, uygulama yapısı (`accounts`, `students`, `documents`, `validation`, `readers`, `internship_forms`, `exports`)
- [x] E-posta ile giriş yapan özel `User` modeli, `ROLE_STUDENT` / `ROLE_ADMIN`, JWT kimlik doğrulama
- [x] Rol tabanlı permission sınıfları (`RolePermission` → `IsStudent`, `IsAdmin`)
- [x] Öğrenci veri seti: `StudentProfile`, CSV içe aktarma (API + `import_students` komutu)
- [x] Kayıt yalnızca veri setindeki öğrenci numarasıyla
- [x] `Document` modeli, statü akışı (`DocumentWorkflow`), model seviyesinde akış koruması
- [x] Dosya doğrulama: uzantı, boyut, içerik imzası
- [x] `DocumentReader` soyutlaması + `MockDocumentReader` (yalnızca test)
- [x] `PdfFormReader`: gerçek Ek-16 şablonunu (KOÜ Mühendislik Fakültesi Staj Kabul Formu) tablo
      hücrelerinden okur; Ek-16 olmayan / taranmış belgeyi gerekçesiyle reddeder
- [x] `BaseValidator` hiyerarşisi (13 denetleyici sınıfı, formun dipnot kuralları dahil), `ValidationEngine`, `ValidationReport` (geçmiş saklanır)
- [x] Staj planı: iş günü hesabı, resmî tatiller, cumartesi çalışma
- [x] Tamamlandı belge kilidi (öğrenci değiştiremez/silemez; admin günceller/siler)
- [x] Türkçe JSON hata biçimi
- [x] React + Vite arayüzü: giriş/kayıt, öğrenci belgeleri, admin belgeler/öğrenciler
- [x] Testler: 186 backend testi (her denetleyici için test; gerçek şablonla okuyucu testleri)

## Aşama 2 — Final

- [ ] **Taranmış belge okuyucu (Gemini)** (`readers/gemini.py`): Kaşeli/imzalı form genelde taranarak
      gelir; `PdfFormReader` bunları okuyamaz. Model ham metinleri döndürür, `Ek16Data.from_raw` aynı
      ayrıştırma ve denetimi uygular. Öğrencinin kişisel verisi (T.C. no) dış servise gideceği için
      KVKK kararı gerekir. Önerilen düzen: önce `pdf`, metin yoksa Gemini (yedekli okuyucu).
- [ ] **Asenkron denetim**: Gerçek okuyucu saniyeler sürebilir; yükleme "Yüklendi"de kalıp denetim
      arka planda (Celery/RQ veya Django tasks) çalışmalı. Şu an istek içinde, senkron.
- [ ] **Ek-17 üretimi** (`exports/`): `Ek17Exporter` alt sınıfı + admin uç noktası/arayüzü.
- [ ] **Google Form kontrol/gönderim** (`internship_forms/`): `InternshipFormGateway` alt sınıfı.
- [ ] PostgreSQL ile çalıştırma ve dağıtım (gunicorn, statik dosyalar, `DEBUG=False` ayarları).
- [ ] Frontend testleri (Vitest + Testing Library).
- [ ] Diyagramların PNG çıktıları ve rapor.

## Netleştirilmesi gerekenler

Bunlar kodda makul varsayımlarla çözüldü; resmî bilgiyle karşılaştırılıp gerekirse düzeltilmeli:

1. **Asgari staj süresi** — varsayılan 20 iş günü (`INTERNSHIP_MIN_WORK_DAYS`). Formda yazmıyor.
2. **"Hafta sonu çalışılıyor mu = E"** — cumartesi iş günü sayılıyor, pazar sayılmıyor.
3. **25 yaş notu** — formdaki "(*) 25 yaş ve üstü ... 6 nolu seçenek işaretlenir" notu kesin kural mı
   bilinmediği için hata değil **uyarı** olarak uygulandı.
4. **Zorunlu alanlar** — faks ve web adresi isteğe bağlı, diğer tüm alanlar zorunlu kabul edildi.
   Staj danışmanı onay kutusu yükleme anında boş olacağı için denetlenmiyor.
5. **Dini bayramlar** — yıla göre değiştiği için `INTERNSHIP_EXTRA_HOLIDAYS` ile elle girilir.
6. **"Staj planı"nın kapsamı** — tarih/iş günü hesabı olarak yorumlandı
   (`documents/services/internship_plan.py`). Ayrı bir plan belgesi kastediliyorsa eklenmeli.
7. **Onaylandı → Tamamlandı** — şu an admin elle yapıyor. Final'de Google Form gönderimine bağlanabilir.
8. **Öğrenci veri seti biçimi** — CSV sütunları `ogrenci_no;ad;soyad;tc_kimlik_no;bolum;sinif;eposta`.
   Okulun gerçek dışa aktarımı farklıysa `StudentDatasetImporter.COLUMNS` güncellenmeli.
9. **KVKK** — T.C. kimlik numarası veri setinde saklanıyor; erişim yalnızca admin'e açık. Saklama
   süresi/maskeleme kararı verilmeli.
