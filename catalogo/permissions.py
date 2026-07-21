from rest_framework.permissions import BasePermission, SAFE_METHODS


class LecturaPublicaEscrituraAutenticada(BasePermission):
    """
    Permite consultas GET sin autenticación.

    Las operaciones POST, PUT, PATCH y DELETE requieren
    un usuario autenticado mediante OAuth 2.0.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(
            request.user
            and request.user.is_authenticated
        )