from django.db import models


class GoogleSheet(models.Model):
    name_report = models.CharField(max_length=100, verbose_name="Используемый отчет")
    name_spreadsheet = models.CharField(max_length=100, verbose_name="Название книги")
    spreadsheet_id = models.CharField(max_length=100)
    sheet_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Google Таблица"
        verbose_name_plural = "Google Таблицы"

    def __str__(self):
        return f"{self.name_report} ({self.name_spreadsheet})"
