import re

import gspread
from google.oauth2.service_account import Credentials
from config import GOOGLE_SHEET_ID, GOOGLE_CREDENTIALS_FILE

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _parse_sheet_id(raw):
    """Extract the spreadsheet ID from a full URL or return as-is."""
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", raw)
    return match.group(1) if match else raw.strip()


def _get_worksheet():
    creds = Credentials.from_service_account_file(GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    sheet_id = _parse_sheet_id(GOOGLE_SHEET_ID)
    spreadsheet = client.open_by_key(sheet_id)
    return spreadsheet.sheet1


def get_pending_leads():
    ws = _get_worksheet()
    records = ws.get_all_records()
    headers = ws.row_values(1)
    status_col = headers.index("status") + 1

    leads = []
    for i, row in enumerate(records):
        if not str(row.get("status", "")).strip():
            leads.append({
                "row_number": i + 2,  # +1 for header, +1 for 1-based index
                "name": str(row.get("name", "")).strip(),
                "email": str(row.get("email", "")).strip(),
                "phone": str(row.get("phone", "")).strip(),
                "campaignId": str(row.get("campaignId", "")).strip(),
            })
    return leads, ws, status_col


def update_row_status(ws, row_number, status_col, status):
    ws.update_cell(row_number, status_col, status)
