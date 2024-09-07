from django.db import models
from django.utils.translation import gettext_lazy as _


class TypeStaff(models.Model):
    type_staff = models.CharField(_("Type staff"), max_length=50)

    def __str__(self):
        return self.type_staff


class CategoryLibraryStaff(models.Model):
    category = models.CharField(_("Category"), max_length=50)
    type_staff = models.ManyToManyField(
        TypeStaff,
        verbose_name=_("Type staff"),
    )

    def __str__(self):
        return self.category


class LibraryStaff(models.Model):
    name = models.CharField(_("Name"), max_length=50)
    link = models.URLField(_("Link"))
    category = models.ForeignKey(
        CategoryLibraryStaff,
        on_delete=models.CASCADE,
    )
    type_staff = models.ManyToManyField(
        TypeStaff,
        verbose_name=_("Type staff"),
    )

    def __str__(self):
        return self.name
