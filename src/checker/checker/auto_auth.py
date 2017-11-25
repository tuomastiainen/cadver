class User:
    is_superuser = True
    is_active = True
    is_staff = True
    id = 1
    pk = 1

def return_true(*args, **kwargs):
    return True

User.has_module_perms = return_true
User.has_perm = return_true
User.is_authenticated = return_true

from django.utils.deprecation import MiddlewareMixin


class AutoAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = User()
