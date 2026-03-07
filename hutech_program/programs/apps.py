from django.apps import AppConfig


class ProgramsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hutech_program.programs"
    verbose_name = "Chương trình đào tạo"

    def ready(self):
        import hutech_program.programs.signals  # noqa: F401

