from audit_log import log_event
from dispatch_db import init_dispatch_log_table, write_dispatch_log

DISPATCH_LOG = []

init_dispatch_log_table()


def send_sms(to: str, message: str, complaint_id: str = None) -> dict:
    result = {"channel": "sms", "to": to, "message": message, "status": "SENT"}
    DISPATCH_LOG.append(result)
    log_event("ALERT_DISPATCH", "system", "SUCCESS", detail=f"SMS to {to}")
    write_dispatch_log(
        complaint_id=complaint_id,
        channel="sms",
        recipient=to,
        delivery_status="SENT",
        raw_response=result,
    )
    return result


def send_email(to: str, subject: str, message: str, complaint_id: str = None) -> dict:
    result = {
        "channel": "email",
        "to": to,
        "subject": subject,
        "message": message,
        "status": "SENT",
    }
    DISPATCH_LOG.append(result)
    log_event("ALERT_DISPATCH", "system", "SUCCESS", detail=f"Email to {to}")
    write_dispatch_log(
        complaint_id=complaint_id,
        channel="email",
        recipient=to,
        delivery_status="SENT",
        raw_response=result,
    )
    return result


def send_webhook(url: str, payload: dict, complaint_id: str = None) -> dict:
    result = {"channel": "webhook", "url": url, "payload": payload, "status": "SENT"}
    DISPATCH_LOG.append(result)
    log_event("ALERT_DISPATCH", "system", "SUCCESS", detail=f"Webhook to {url}")
    write_dispatch_log(
        complaint_id=complaint_id,
        channel="webhook",
        recipient=url,
        delivery_status="SENT",
        raw_response=result,
    )
    return result


def dispatch_alert(zone: str, risk_level: str, recipients: dict, complaint_id: str = None) -> list:
    results = []
    message = f"High-risk zone detected: {zone} (risk: {risk_level})"

    if "phone" in recipients:
        results.append(send_sms(recipients["phone"], message, complaint_id))
    if "email" in recipients:
        results.append(
            send_email(recipients["email"], "CyberSight Alert", message, complaint_id)
        )
    if "webhook_url" in recipients:
        results.append(
            send_webhook(
                recipients["webhook_url"],
                {"zone": zone, "risk": risk_level},
                complaint_id,
            )
        )

    return results