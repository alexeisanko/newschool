from django.contrib import admin

from .models import Student
from .models import Subject


class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "id_my_class", "vk_link")
    search_fields = ("name", "vk_link")
    list_filter = ("id_my_class",)


class SubjectAdmin(admin.ModelAdmin):
    list_display = ("subject", "student", "id_my_class")
    search_fields = ("subject", "student__name")
    list_filter = ("id_my_class",)


admin.site.register(Student, StudentAdmin)
admin.site.register(Subject, SubjectAdmin)
