from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RbacConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hutech_program.rbac"
    verbose_name = _("Phân quyền & Vai trò")
