import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MyClassConfig(AppConfig):
    name = "newschool.myclass"
    verbose_name = _("MyClass")

    def ready(self):
        with contextlib.suppress(ImportError):
            import newschool.myclass.signals  # noqa: F401
