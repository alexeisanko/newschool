from django.conf import settings
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from pandas import DataFrame

SERVICE_ACCOUNT_FILE = settings.APPS_DIR / "credentials" / "client_secret.json"


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def get_last_row(spreadsheet_id: str, sheet_name: str):
    service = get_service()
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()
    )
    values = result.get("values", [])
    return len(values) + 1


def append_dataframe_to_sheet(
    spreadsheet_id: str,
    sheet_name: str,
    dataframe: DataFrame,
):
    service = get_service()
    sheet = service.spreadsheets()

    values = dataframe.to_numpy().tolist()

    last_row = get_last_row(spreadsheet_id, sheet_name)

    range_name = f"{sheet_name}!A{last_row}"

    # Вставляем данные
    body = {"values": values}
    return (
        sheet.values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body,
            insertDataOption="INSERT_ROWS",
        )
        .execute()
    )
