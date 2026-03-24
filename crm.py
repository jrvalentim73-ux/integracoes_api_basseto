import requests
from config import CRM_API_KEY, CRM_ENDPOINT


def send_lead(lead):
    payload = {
        "name": lead["name"],
        "email": lead["email"],
        "phone": str(lead["phone"]),
        "campaignId": lead["campaignId"],
    }
    headers = {
        "X-API-Key": CRM_API_KEY,
        "Content-Type": "application/json",
    }
    try:
        resp = requests.post(CRM_ENDPOINT, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            return {"success": True, "detail": "OK"}
        return {"success": False, "detail": f"HTTP {resp.status_code}: {resp.text[:200]}"}
    except requests.RequestException as e:
        return {"success": False, "detail": str(e)}
