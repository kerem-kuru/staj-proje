# Rapor Notları

## NYP ilkelerinin kodda karşılığı

### Soyutlama (Abstraction)

| Soyut tip | Dosya | Neyi gizler |
|-----------|-------|-------------|
| `DocumentReader` | `backend/readers/base.py` | Belgenin nasıl okunduğunu (PDF tablo okuma, mock, ileride Gemini) |
| `BaseValidator` | `backend/validation/validators/base.py` | Her kuralın iç mantığını; motor yalnızca `validate()` bilir |
| `FieldFormatValidator` | `backend/validation/validators/base.py` | "Tek alan biçim kontrolü" kalıbını |
| `DocumentPolicy` | `backend/documents/policies.py` | Rol bazlı erişim kurallarını |
| `StudentDatasetImporter` | `backend/students/services.py` | Veri seti dosya biçimini (CSV, ileride Excel) |
| `Ek17Exporter`, `InternshipFormGateway` | `backend/exports/services.py`, `backend/internship_forms/services.py` | Final aşamasındaki dış sistemleri |

### Kalıtım (Inheritance)

- `BaseValidator` → `FieldFormatValidator` → `NationalIdValidator` / `EmailFormatValidator` / `PhoneFormatValidator`
  (iki seviyeli hiyerarşi; ortak `validate()` üst sınıfta, alana özgü `is_valid_value()` alt sınıfta).
- `RolePermission` → `IsStudent`, `IsAdmin` (`backend/accounts/permissions.py`): alt sınıflar yalnızca
  `required_role` ve mesajı belirler.
- `User(AbstractUser)` (`backend/accounts/models.py`), `InvalidStatusTransition(APIException)`,
  `DocumentLocked(PermissionDenied)` (`backend/documents/exceptions.py`).

### Çok biçimlilik (Polymorphism)

- `ValidationEngine.run()` (`backend/validation/engine.py`) listedeki her nesnede `validate()` çağırır;
  hangi alt sınıf olduğunu bilmez. Testte `AlwaysWarns` / `AlwaysFails` gibi yeni alt sınıflar motoru
  değiştirmeden eklenir (`backend/validation/tests/test_engine.py`).
- `DocumentService` okuyucuyu `DocumentReader` olarak alır; `PdfFormReader`, `MockDocumentReader` ya da ileride
  Gemini verilmesi servis kodunu değiştirmez. Tüm okuyucular aynı `Ek16Data`'yı üretir.
- `policy_for(user)` öğrenciye `StudentDocumentPolicy`, admin'e `AdminDocumentPolicy` döndürür; servis ve
  serializer aynı `can_delete()` / `can_modify()` çağrısıyla farklı davranış alır.
- `EmailFormatValidator("student_email")` ve `EmailFormatValidator("company_email")`: aynı sınıf, farklı yapılandırma.

### Kapsülleme (Encapsulation)

- `Document` statüsü dışarıdan doğrudan değiştirilmez: `transition_to()` kullanılır, `save()` akışa aykırı
  değişikliği reddeder (`backend/documents/models.py`). Geçiş tablosu `DocumentWorkflow._TRANSITIONS`
  salt-okunur `MappingProxyType` (`backend/documents/workflow.py`).
- `ValidationResult._issues` özel liste; dışarıya yalnızca değiştirilemez `tuple` döner (`backend/validation/types.py`).
- `ValidationIssue` `frozen` dataclass; oluşturulduktan sonra değiştirilemez.
- `DocumentService` okuyucu ve motoru `_reader` / `_engine` olarak saklar; view'lar yalnızca public metotları görür.
- `PdfFormReader` sayfa ayrıştırmayı dışarıya kapalı `_Ek16Page` sınıfına bırakır; dışarıya yalnızca `read()` açıktır.

## Katmanlar

```
View (HTTP, serializer)  →  Service (iş kuralı, transaction)  →  Model / Reader / Validator
```

View'lar iş kuralı içermez; örn. "tamamlanan belge silinemez" kuralı `DocumentService.delete()` +
`StudentDocumentPolicy.can_delete()` içindedir ve view yalnızca servisi çağırır.

## Test özeti

`cd backend && pytest` → 186 test. Her denetleyici için ayrı dosya:

| Denetleyici | Test dosyası |
|-------------|--------------|
| RequiredFieldsValidator, UnparsedValuesValidator | `validation/tests/test_required_fields.py` |
| NationalIdValidator, EmailFormatValidator, PhoneFormatValidator | `validation/tests/test_formats.py` |
| StudentIdentityValidator | `validation/tests/test_student_identity.py` |
| InternshipDatesValidator, WorkDaysValidator | `validation/tests/test_internship.py` |
| HealthStatusValidator, InternshipConditionsValidator | `validation/tests/test_declarations.py` |
| SignatureValidator | `validation/tests/test_signature.py` |
| ValidationEngine | `validation/tests/test_engine.py` |
| Dosya doğrulayıcıları | `documents/tests/test_file_validators.py` |

Ayrıca: gerçek Ek-16 şablonuyla PDF okuyucu (`readers/tests/test_pdf_form_reader.py`), değer ayrıştırıcıları, statü akışı, staj planı hesabı, belge API'si (rol ve kilit kuralları), kayıt/giriş, CSV içe aktarma, mock okuyucu.
