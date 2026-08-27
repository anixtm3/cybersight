from audit_log import log_event

DISPATCH_LOG = []


def send_sms(to: str, message: str) -> dict:
    result = {"channel": "sms", "to": to, "message": message, "status": "SENT"}
    DISPATCH_LOG.append(result)
    log_event("ALERT_DISPATCH", "system", "SUCCESS", detail=f"SMS to {to}")
    return result


def send_email(to: str, subject: str, message: str) -> dict:
    result = {
        "channel": "email",
        "to": to,
        "subject": subject,
        "message": message,
        "status": "SENT",
    }
    DISPATCH_LOG.append(result)
    log_event("ALERT_DISPATCH", "system", "SUCCESS", detail=f"Email to {to}")
    return result


def send_webhook(url: str, payload: dict) -> dict:
    result = {"channel": "webhook", "url": url, "payload": payload, "status": "SENT"}
    DISPATCH_LOG.append(result)
    log_event("ALERT_DISPATCH", "system", "SUCCESS", detail=f"Webhook to {url}")
    return result


def dispatch_alert(zone: str, risk_level: str, recipients: dict) -> list:
    results = []
    message = f"High-risk zone detected: {zone} (risk: {risk_level})"

    if "phone" in recipients:
        results.append(send_sms(recipients["phone"], message))
    if "email" in recipients:
        results.append(send_email(recipients["email"], "CyberSight Alert", message))
    if "webhook_url" in recipients:
        results.append(
            send_webhook(recipients["webhook_url"], {"zone": zone, "risk": risk_level})
        )

    return results