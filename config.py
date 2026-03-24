import os
from dotenv import load_dotenv

load_dotenv()

CRM_API_KEY = os.environ["CRM_API_KEY"]
CRM_ENDPOINT = "https://crmbassetobackend.up.railway.app/webhooks/lead"
GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
DEFAULT_CAMPAIGN_ID = os.environ.get("CAMPAIGN_ID", "")
