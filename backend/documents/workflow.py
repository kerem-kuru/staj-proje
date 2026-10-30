"""Belge statü akışı.

Yüklendi -> İnceleniyor -> Hatalı/Eksik -> (yeniden yükleme) Yüklendi ...
                        └-> Onaylandı -> Tamamlandı
Geçiş kuralları yalnızca bu sınıfta tutulur (kapsülleme); model ve servisler
statüyü doğrudan değil, bu sınıf üzerinden değiştirir.
"""
from types import MappingProxyType
from typing import Final

from django.db import models

from .exceptions import InvalidStatusTransition


class DocumentStatus(models.TextChoices):
    UPLOADED = "YUKLENDI", "Yüklendi"
    IN_REVIEW = "INCELENIYOR", "İnceleniyor"
    REJECTED = "HATALI_EKSIK", "Hatalı/Eksik"
    APPROVED = "ONAYLANDI", "Onaylandı"
    COMPLETED = "TAMAMLANDI", "Tamamlandı"


class DocumentWorkflow:
    _TRANSITIONS: Final = MappingProxyType(
        {
            DocumentStatus.UPLOADED: frozenset({DocumentStatus.IN_REVIEW}),
            DocumentStatus.IN_REVIEW: frozenset({DocumentStatus.REJECTED, DocumentStatus.APPROVED}),
            DocumentStatus.REJECTED: frozenset({DocumentStatus.UPLOADED}),
            # Admin onaylanmış belgeyi tamamlayabilir ya da gerekçeyle geri çevirebilir.
            DocumentStatus.APPROVED: frozenset({DocumentStatus.COMPLETED, DocumentStatus.REJECTED}),
            DocumentStatus.COMPLETED: frozenset(),
        }
    )

    @classmethod
    def allowed_targets(cls, current: str) -> frozenset[str]:
        return cls._TRANSITIONS.get(DocumentStatus(current), frozenset())

    @classmethod
    def can_transition(cls, current: str, target: str) -> bool:
        return target in cls.allowed_targets(current)

    @classmethod
    def ensure_transition(cls, current: str, target: str) -> None:
        if not cls.can_transition(current, target):
            raise InvalidStatusTransition(
                f"'{DocumentStatus(current).label}' statüsündeki belge "
                f"'{DocumentStatus(target).label}' statüsüne geçirilemez."
            )
