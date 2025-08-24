from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteSection(models.Model):
    name = models.CharField(_("Section name"), max_length=100)
    url_name = models.CharField(_("URL name"), max_length=100)
    icon = models.CharField(_("Icon class"), max_length=50, blank=True)
    order = models.PositiveIntegerField(_("Order"), default=0)
    is_active = models.BooleanField(_("Is active"), default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class TypeStaff(models.Model):
    type_staff = models.CharField(_("Type staff"), max_length=50)
    site_sections = models.ManyToManyField(
        SiteSection,
        verbose_name=_("Site sections access"),
        blank=True,
    )

    def __str__(self):
        return self.type_staff


class CategoryLibraryStaff(models.Model):
    category = models.CharField(_("Category"), max_length=50)
    type_staff = models.ManyToManyField(
        TypeStaff,
        verbose_name=_("Type staff"),
    )
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ['order', 'category']

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
    order = models.PositiveIntegerField(_("Order"), default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
