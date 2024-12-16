from datetime import UTC
from datetime import datetime

from celery import shared_task

from newschool.google_sheets.models import GoogleSheet
from newschool.google_sheets.service import append_dataframe_to_sheet
from newschool.reports.workload_teachers import calculate_statistic_teacher


@shared_task()
def save_workload_teacher():
    current_date = datetime.now(tz=UTC).date().isoformat()

    data = calculate_statistic_teacher(current_date)
    data.insert(0, "Дата", current_date)

    google_sheet = GoogleSheet.objects.get(
        name_report="Ежедневный отчет по репетиторам",
    )
    append_dataframe_to_sheet(
        google_sheet.spreadsheet_id,
        google_sheet.sheet_name,
        data,
    )
