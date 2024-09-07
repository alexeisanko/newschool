import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StaffConfig(AppConfig):
    name = "newschool.staff"
    verbose_name = _("Staff")

    def ready(self):
        with contextlib.suppress(ImportError):
            import newschool.staff.signals  # noqa: F401
