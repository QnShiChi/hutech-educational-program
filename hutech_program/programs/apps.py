from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ProgramsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hutech_program.programs"
    verbose_name = _("Chương trình đào tạo")

    def ready(self):
        import hutech_program.programs.signals  # noqa: F401

