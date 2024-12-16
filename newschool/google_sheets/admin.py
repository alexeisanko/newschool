from django.contrib import admin

from .models import GoogleSheet


class GoogleSheetAdmin(admin.ModelAdmin):
    list_display = (
        "name_report",
        "name_spreadsheet",
        "spreadsheet_id",
        "sheet_name",
    )
    search_fields = (
        "name_report",
        "name_spreadsheet",
    )


admin.site.register(GoogleSheet, GoogleSheetAdmin)
