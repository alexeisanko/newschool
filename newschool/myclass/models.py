from django.db import models
from django.utils.translation import gettext_lazy as _


class Teacher(models.Model):
    id = models.IntegerField(_("Teacher id"))
    name = models.CharField(_("Full name"), max_length=50)
    is_work = models.BooleanField(_("Is work?"))

    def __str__(self):
        return self.name


class Lesson(models.Model):
    id = models.IntegerField(_("Lesson id"))
    date = models.DateField(_("Date"), auto_now=False, auto_now_add=False)
    status = models.BooleanField(_("status lesson"))
    teacher = models.ForeignKey(
        Teacher, verbose_name=_("teacher"), on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.pk}. {self.teacher.name} ({self.date})"


class Record(models.Model):
    id = models.IntegerField(_("Record id"))
    student = models.IntegerField(_("Student id"))
    lesson = models.ForeignKey(
        Lesson, verbose_name=_("Lesson"), on_delete=models.CASCADE
    )
    free = models.BooleanField(_("is free lesson?"))
    visit = models.BooleanField(_("is student visit?"))
    good_reason = models.BooleanField(_("is good reason skip?"))
    test = models.BooleanField(_("is test lesson?"))
    skip = models.BooleanField(_("is skip lesson?"))
    paid = models.BooleanField(_("is paid lesson?"))
