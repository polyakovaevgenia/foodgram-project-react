from rest_framework import permissions


class RoleAdminrOrReadOnly(permissions.BasePermission):
    """Доступ на чтение всем. Полный доступ админу и суперпользователю."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated
            and request.user.is_admin
        )


class AuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
                request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
            )

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsAdminIsAuthorOrReadOnly(permissions.BasePermission):
    """Доступ на чтение всем. Полный доступ автору и админу."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (obj.author == request.user or request.user.is_admin
                    or request.user.is_moderator))
