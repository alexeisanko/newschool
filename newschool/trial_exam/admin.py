from django.contrib import admin

from .models import ExamConfig
from .models import ExamRegistration
from .models import ExamSchedule
from .models import ExamType
from .models import MessageBot
from .models import Subject
from .models import WeekDay


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ("type",)
    list_filter = ("type",)
    search_fields = ("type",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active", "types")
    search_fields = ("name", "genitive_name")


@admin.register(WeekDay)
class WeekDayAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ("weekday", "start_exam", "end_exam", "available_slots")
    list_filter = ("weekday",)
    search_fields = ("weekday__name",)


@admin.register(ExamRegistration)
class ExamRegistrationAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "date", "time_exam")
    list_filter = ("subject", "date")
    search_fields = ("user__username", "subject__name")


@admin.register(ExamConfig)
class ExamConfigAdmin(admin.ModelAdmin):
    list_display = ("is_active", "registration_open_day", "registration_close_day")
    list_filter = ("is_active",)
    search_fields = ("registration_open_day", "registration_close_day")


@admin.register(MessageBot)
class MessageBotAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title", "message")
