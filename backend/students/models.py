from django.conf import settings
from django.db import models


class StudentProfile(models.Model):
    """Okulun öğrenci veri setinden içe aktarılan kayıt.

    Öğrenci sisteme kayıt olduğunda profil `user` ile eşleşir. Belge denetiminde
    Ek-16'daki kimlik bilgileri bu kayıtla karşılaştırılır.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="kullanıcı",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_profile",
    )
    student_number = models.CharField("öğrenci numarası", max_length=20, unique=True)
    first_name = models.CharField("ad", max_length=150)
    last_name = models.CharField("soyad", max_length=150)
    national_id = models.CharField("T.C. kimlik numarası", max_length=11, blank=True)
    department = models.CharField("bölüm", max_length=150)
    class_year = models.PositiveSmallIntegerField("sınıf", null=True, blank=True)
    email = models.EmailField("e-posta", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student_number"]
        verbose_name = "öğrenci profili"
        verbose_name_plural = "öğrenci profilleri"

    def __str__(self) -> str:
        return f"{self.student_number} - {self.full_name}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
