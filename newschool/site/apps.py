import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SiteConfig(AppConfig):
    name = "newschool.site"
    verbose_name = _("Site")

    def ready(self):
        with contextlib.suppress(ImportError):
            import newschool.site.signals  # noqa: F401
