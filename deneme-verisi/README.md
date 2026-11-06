# Deneme verisi

Öğrenciler ve belgeler kurgusaldır. Belgeler boş Ek-16 şablonundan `uret.py` ile üretildi; bu dosya da
aynı betikle yazılır, elle değiştirmeyin. Senaryolar `backend/documents/tests/test_deneme_verisi.py`
tarafından otomatik olarak da çalıştırılır.

## Adımlar

1. `backend` klasöründe `python manage.py migrate` ve gerekirse `python manage.py seed_demo` çalıştırın.
2. `admin@staj.local` / `Admin.12345` ile girin. **Öğrenci Veri Seti** sayfasından
   `ogrenci_veri_seti.csv` dosyasını içe aktarın.
3. Çıkış yapıp **Öğrenci kaydı** sayfasından denemek istediğiniz öğrenciyi kaydedin. Ad, soyad, e-posta ve
   numara aşağıdaki gibi olmalı; şifre olarak `Deneme.12345` kullanabilirsiniz. `seed_demo` çalıştıysa Ayşe
   zaten kayıtlıdır: `ayse@ogrenci.edu.tr` / `Ogrenci.12345`.
4. Öğrenci hesabıyla **Staj planı** alanını tablodaki gibi seçin, `belgeler/` klasöründeki dosyayı yükleyin.

Beş kez yanlış şifre girerseniz hesap 15 dakika kilitlenir; bu da denenecek bir kuraldır.

## Öğrenciler

| Ad soyad | Numara | E-posta | Uyruk |
|----------|--------|---------|-------|
| Ayşe Yılmaz | 220101001 | ayse@ogrenci.edu.tr | T.C. |
| İsmail Kaya | 220101002 | ismail@ogrenci.edu.tr | T.C. |
| Zeynep Demir | 220101003 | zeynep@ogrenci.edu.tr | T.C. |
| Elvin Mammadov | 220101004 | elvin@ogrenci.edu.tr | Azerbaycan |
| Fatma Şahin | 220101005 | fatma@ogrenci.edu.tr | T.C. |
| Can Aydın | 220101006 | can@ogrenci.edu.tr | T.C. |

## Belgeler

`19_hata_30_gun_kurali.pdf` dışındaki senaryolar 14 Mayıs 2027'ye kadar aynı sonucu verir; bu tarihten
sonra 30 gün kuralına takılırlar.

| Dosya | Hesap | Seçilecek plan | Beklenen | Ne deniyor |
|-------|-------|----------------|----------|------------|
| `01_gecerli_ayse.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Onaylandı | Tüm kurallara uyan form |
| `02_gecerli_yabanci_elvin.pdf` | Elvin | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Onaylandı | Yabancı uyruk, 99 ile başlayan numara |
| `03_gecerli_haftada_3_gun_zeynep.pdf` | Zeynep | 14.06.2027 - 28.07.2027 (Pzt, Sal, Çar) | Onaylandı | Haftada 3 gün staj planı |
| `04_uyari_az_muhendis_ismail.pdf` | İsmail | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Onaylandı | 3 mühendis: onaylanır, mezun olunan bölüm sorulur |
| `05_uyari_ucretli_yurtdisi_fatma.pdf` | Fatma | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Onaylandı | 25 yaş üstü, ücretli ve yurtdışı staj: hatırlatma uyarıları |
| `10_hata_bos_form.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Hiç doldurulmamış Ek-16 |
| `11_hata_tc_kimlik.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | T.C. kimlik numarası algoritmadan geçmiyor |
| `12_hata_yabanci_99_degil_elvin.pdf` | Elvin | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Yabancı uyruk ama numara 99 ile başlamıyor |
| `13_hata_veri_seti_uyusmuyor.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Ad soyad ve doğum tarihi veri setinden farklı |
| `14_hata_telefon_bicimi.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Telefon +90 xxx xxx xx xx biçiminde değil |
| `15_hata_adres_eksik.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Adreste sokak, bina ve daire no yok |
| `16_hata_ogretim_yili_ardisik_degil.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | 2026-2028: yıllar ardışık değil |
| `17_hata_yariyil_yok.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Öğretim yılında yarıyıl yazmıyor |
| `18_hata_tarih_ogretim_yili_disinda.pdf` | Ayşe | 04.10.2027 - 01.11.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Staj Ekim 2027'de, öğretim yılı 2026-2027 |
| `19_hata_30_gun_kurali.pdf` | Ayşe | 16.11.2026 - 11.12.2026 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Staja 30 günden az kaldı; önerilen tarih gösterilir |
| `20_hata_gun_sayisi.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Formda 25 gün yazıyor, hesaplanan 20 |
| `21_hata_plan_tarihi_uyusmuyor.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Formdaki tarihler seçilen plandan farklı |
| `22_hata_ogrenci_onayi_dolu.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Öğrenci onay kısmı doldurulmuş |
| `23_hata_danisman_onayi_dolu.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Staj danışmanı onay kısmı doldurulmuş |
| `24_hata_kase_imza_yok.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | İşveren kaşesi ve imzası yok |
| `25_hata_isveren_alani_bos.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | İşveren adı soyadı boş |
| `26_hata_muhendis_sifir.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Mühendis sayısı 0 |
| `30_okunamaz_baska_belge.pdf` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Ek-16 olmayan PDF |
| `31_okunamaz_goruntu.png` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | PNG kabul edilir; OCR final aşamasında |
| `32_okunamaz_word.docx` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Hatalı/Eksik | Word kabul edilir; okuma final aşamasında |
| `33_reddedilir_format.txt` | Ayşe | 14.06.2027 - 09.07.2027 (Pzt, Sal, Çar, Per, Cum) | Yüklenmez | Desteklenmeyen dosya türü, yüklenmez |
