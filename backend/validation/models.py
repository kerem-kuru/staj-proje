from django.db import models


class ValidationReport(models.Model):
    """Bir belgenin bir revizyonu için üretilen denetim raporu. Geçmiş raporlar silinmez."""

    document = models.ForeignKey(
        "documents.Document", verbose_name="belge", on_delete=models.CASCADE, related_name="reports"
    )
    revision = models.PositiveIntegerField("revizyon")
    is_valid = models.BooleanField("geçerli mi")
    summary = models.CharField("özet", max_length=255)
    issues = models.JSONField("bulgular", default=list)
    reader_name = models.CharField("okuyucu", max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        verbose_name = "denetim raporu"
        verbose_name_plural = "denetim raporları"

    def __str__(self) -> str:
        return f"Rapor #{self.pk} - {self.summary}"
