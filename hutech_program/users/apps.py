from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    name = "hutech_program.users"
    verbose_name = _("Người dùng")

    def ready(self):
        """
        Override this method in subclasses to run code when Django starts.
        """
