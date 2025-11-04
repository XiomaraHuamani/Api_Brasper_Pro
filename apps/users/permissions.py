from rest_framework.permissions import BasePermission

class IsStaff(BasePermission):
    """
    Permiso para usuarios con el rol 'staff'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == 'staff'


class IsClient(BasePermission):
    """
    Permiso para usuarios con el rol 'client'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == 'client'


class IsSales(BasePermission):
    """
    Permiso para usuarios con el rol 'sales'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role and request.user.role.name == 'sales'
    
class IsOwnerOrStaff(BasePermission):
    """
    Permiso que permite acceso si:
    1. El usuario es staff
    2. El usuario es el propietario del objeto
    """
    def has_object_permission(self, request, view, obj):
        # Staff siempre tiene acceso
        if request.user.role and request.user.role.name == 'staff':
            return True
        
        # Verificar si el objeto tiene atributo user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
            
        return False