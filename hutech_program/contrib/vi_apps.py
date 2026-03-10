"""Custom AppConfig overrides for third-party apps to provide Vietnamese names."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class VietnameseAccountConfig(AppConfig):
    """Override allauth.account app label for Vietnamese admin."""
    name = "allauth.account"
    verbose_name = _("Tài khoản")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        super().ready()
        try:
            from allauth.account.models import EmailAddress
            EmailAddress._meta.verbose_name = _("Địa chỉ email")
            EmailAddress._meta.verbose_name_plural = _("Các địa chỉ email")
        except ImportError:
            pass


class VietnameseMfaConfig(AppConfig):
    """Override allauth.mfa app label for Vietnamese admin."""
    name = "allauth.mfa"
    verbose_name = _("Xác thực đa yếu tố")
    default_auto_field = "django.db.models.BigAutoField"
    
    def ready(self):
        super().ready()
        try:
            from allauth.mfa.models import Authenticator
            Authenticator._meta.verbose_name = _("Bộ xác thực")
            Authenticator._meta.verbose_name_plural = _("Các bộ xác thực")
        except ImportError:
            pass


class VietnameseCeleryBeatConfig(AppConfig):
    """Override django_celery_beat app label for Vietnamese admin."""
    name = "django_celery_beat"
    verbose_name = _("Tác vụ định kỳ")

    def ready(self):
        super().ready()
        try:
            from django_celery_beat.models import ClockedSchedule, CrontabSchedule, IntervalSchedule, PeriodicTask, SolarSchedule
            ClockedSchedule._meta.verbose_name = _("Lên lịch thao tác")
            ClockedSchedule._meta.verbose_name_plural = _("Lịch được thiết lập")
            CrontabSchedule._meta.verbose_name = _("Lên lịch Crontab")
            CrontabSchedule._meta.verbose_name_plural = _("Schedules Crontab")
            IntervalSchedule._meta.verbose_name = _("Khoảng thời gian")
            IntervalSchedule._meta.verbose_name_plural = _("Các khoảng thời gian")
            PeriodicTask._meta.verbose_name = _("Tác vụ định kỳ")
            PeriodicTask._meta.verbose_name_plural = _("Các tác vụ định kỳ")
            SolarSchedule._meta.verbose_name = _("Lịch sự kiện năng lượng mặt trời")
            SolarSchedule._meta.verbose_name_plural = _("Schedules năng lượng mặt trời")
        except ImportError:
            pass


class VietnameseSocialAccountConfig(AppConfig):
    """Override allauth.socialaccount app label for Vietnamese admin."""
    name = "allauth.socialaccount"
    verbose_name = _("Tài khoản mạng xã hội")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        super().ready()
        try:
            from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
            SocialAccount._meta.verbose_name = _("Tài khoản mạng xã hội")
            SocialAccount._meta.verbose_name_plural = _("Các tài khoản mạng xã hội")
            SocialApp._meta.verbose_name = _("Ứng dụng mạng xã hội")
            SocialApp._meta.verbose_name_plural = _("Các ứng dụng mạng xã hội")
            SocialToken._meta.verbose_name = _("Token ứng dụng mạng xã hội")
            SocialToken._meta.verbose_name_plural = _("Các token ứng dụng mạng xã hội")
        except ImportError:
            pass


class VietnameseSitesConfig(AppConfig):
    """Override django.contrib.sites app label for Vietnamese admin."""
    name = "django.contrib.sites"
    verbose_name = _("Các trang web")
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        super().ready()
        try:
            from django.contrib.sites.models import Site
            Site._meta.verbose_name = _("Trang web")
            Site._meta.verbose_name_plural = _("Các trang web")
        except ImportError:
            pass
