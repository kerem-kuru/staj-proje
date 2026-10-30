"""Rol bazlı belge erişim politikaları.

Servisler kullanıcının rolünü sorgulamak yerine `policy_for(user)` ile aldığı
politikaya sorar; öğrenci ve admin politikaları aynı arayüzü farklı kurallarla
uygular (çok biçimlilik).
"""
from abc import ABC, abstractmethod

from django.db.models import QuerySet

from accounts.models import User

from .models import Document


class DocumentPolicy(ABC):
    @abstractmethod
    def scope(self, queryset: QuerySet[Document], user: User) -> QuerySet[Document]:
        """Kullanıcının görebileceği belgeler."""

    @abstractmethod
    def can_modify(self, user: User, document: Document) -> bool: ...

    @abstractmethod
    def can_delete(self, user: User, document: Document) -> bool: ...


class StudentDocumentPolicy(DocumentPolicy):
    def scope(self, queryset: QuerySet[Document], user: User) -> QuerySet[Document]:
        return queryset.filter(student__user=user)

    def _owns(self, user: User, document: Document) -> bool:
        return document.student.user_id == user.pk

    def can_modify(self, user: User, document: Document) -> bool:
        return self._owns(user, document) and not document.is_completed

    def can_delete(self, user: User, document: Document) -> bool:
        return self._owns(user, document) and not document.is_completed


class AdminDocumentPolicy(DocumentPolicy):
    def scope(self, queryset: QuerySet[Document], user: User) -> QuerySet[Document]:
        return queryset

    def can_modify(self, user: User, document: Document) -> bool:
        return True

    def can_delete(self, user: User, document: Document) -> bool:
        return True


def policy_for(user: User) -> DocumentPolicy:
    return AdminDocumentPolicy() if user.is_admin else StudentDocumentPolicy()
