# Diyagramlar

GitHub ve VS Code (Markdown Preview Mermaid eklentisi) bu diyagramları doğrudan çizer.
PNG gerekirse: `npx @mermaid-js/mermaid-cli -i diyagramlar.md -o diyagram.png`.

## Belge statü akışı

```mermaid
stateDiagram-v2
    [*] --> Yuklendi: öğrenci yükler
    Yuklendi --> Inceleniyor: sistem okur
    Inceleniyor --> Onaylandi: tüm kurallar geçti
    Inceleniyor --> HataliEksik: hata bulundu
    HataliEksik --> Yuklendi: düzeltilip yeniden yüklenir
    Onaylandi --> Tamamlandi: admin tamamlar
    Onaylandi --> HataliEksik: admin gerekçeyle geri çevirir
    Tamamlandi --> [*]

    Yuklendi: Yüklendi
    Inceleniyor: İnceleniyor
    HataliEksik: Hatalı/Eksik
    Onaylandi: Onaylandı
    Tamamlandi: Tamamlandı (öğrenci için kilitli)
```

## Denetleyici hiyerarşisi (kalıtım + çok biçimlilik)

```mermaid
classDiagram
    class BaseValidator {
        <<abstract>>
        +code: str
        +description: str
        +validate(data, context)* list~ValidationIssue~
        #_issue(field, message, severity)
    }
    class FieldFormatValidator {
        <<abstract>>
        -_field_name: str
        +validate(data, context)
        +is_valid_value(value)* bool
        +error_message(label)* str
    }
    BaseValidator <|-- FieldFormatValidator
    BaseValidator <|-- RequiredFieldsValidator
    BaseValidator <|-- StudentIdentityValidator
    BaseValidator <|-- InternshipDatesValidator
    BaseValidator <|-- WorkDaysValidator
    BaseValidator <|-- SignatureValidator
    BaseValidator <|-- UnparsedValuesValidator
    BaseValidator <|-- HealthStatusValidator
    BaseValidator <|-- InternshipConditionsValidator
    FieldFormatValidator <|-- NationalIdValidator
    FieldFormatValidator <|-- EmailFormatValidator
    FieldFormatValidator <|-- PhoneFormatValidator

    class ValidationEngine {
        -_validators: tuple
        +run(data, context) ValidationResult
    }
    class ValidationResult {
        -_issues: list
        +issues: tuple
        +errors: tuple
        +is_valid: bool
    }
    ValidationEngine o-- BaseValidator
    ValidationEngine ..> ValidationResult
```

## Okuyucu ve politika soyutlamaları

```mermaid
classDiagram
    class DocumentReader {
        <<abstract>>
        +name: str
        +read(document) Ek16Data
        #_extract(content, document)* Ek16Data
    }
    DocumentReader <|-- PdfFormReader
    DocumentReader <|-- MockDocumentReader
    DocumentReader <|-- GeminiDocumentReader

    class DocumentPolicy {
        <<abstract>>
        +scope(queryset, user)*
        +can_modify(user, document)* bool
        +can_delete(user, document)* bool
    }
    DocumentPolicy <|-- StudentDocumentPolicy
    DocumentPolicy <|-- AdminDocumentPolicy

    class RolePermission {
        +required_role: Role
        +has_permission(request, view) bool
    }
    RolePermission <|-- IsStudent
    RolePermission <|-- IsAdmin

    class DocumentService {
        -_reader: DocumentReader
        -_engine: ValidationEngine
        +upload(student, file)
        +reupload(user, document, file)
        +process(document)
        +complete(document)
        +reject(document, note)
        +delete(user, document)
    }
    DocumentService --> DocumentReader
    DocumentService --> ValidationEngine
    DocumentService ..> DocumentPolicy
```

## Veri modeli

```mermaid
erDiagram
    User ||--o| StudentProfile : "hesap"
    StudentProfile ||--o{ Document : "yükler"
    Document ||--o{ ValidationReport : "rapor geçmişi"

    User {
        string email UK
        string role "ROLE_STUDENT | ROLE_ADMIN"
    }
    StudentProfile {
        string student_number UK
        string first_name
        string last_name
        string national_id
        string department
        int class_year
    }
    Document {
        string doc_type "EK16"
        file file
        string status
        int revision
        json extracted_data
        text admin_note
    }
    ValidationReport {
        int revision
        bool is_valid
        string summary
        json issues
        string reader_name
    }
```

## Yükleme akışı

```mermaid
sequenceDiagram
    actor O as Öğrenci
    participant V as DocumentViewSet
    participant S as DocumentService
    participant R as DocumentReader
    participant E as ValidationEngine
    O->>V: POST /api/documents/ (file)
    V->>S: upload(profile, file)
    S->>S: Document oluştur (Yüklendi)
    S->>S: transition_to(İnceleniyor)
    S->>R: read(document)
    R-->>S: Ek16Data
    S->>E: run(data, context)
    E-->>S: ValidationResult
    S->>S: ValidationReport kaydet
    S->>S: transition_to(Onaylandı | Hatalı/Eksik)
    S-->>V: Document
    V-->>O: 201 JSON (statü + rapor)
```
