import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from pii_masking import (
    mask_phone,
    mask_email,
    mask_account_number,
    mask_aadhaar,
    mask_pan,
    mask_address,
)
from password_security import hash_password, verify_password
from rbac import create_token
from alert_dispatch import send_sms, send_email, send_webhook, dispatch_alert


def test_mask_phone():
    assert mask_phone("9876543210") == "XXXXXX3210"


def test_mask_email():
    assert mask_email("victim@example.com") == "v****m@example.com"


def test_mask_account_number():
    assert mask_account_number("123456789012") == "********9012"


def test_mask_aadhaar():
    assert mask_aadhaar("123456789012") == "XXXX XXXX 9012"


def test_mask_pan():
    assert mask_pan("ABCDE1234F") == "ABXXXXXX4F"


def test_mask_address():
    result = mask_address("123 MG Road, Delhi")
    assert result == "*** Delhi"


def test_password_hash_and_verify():
    hashed = hash_password("mypassword123")
    assert verify_password("mypassword123", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_rbac_token_roundtrip():
    token = create_token("user1", "investigator")
    assert isinstance(token, str)
    assert len(token) > 0


def test_send_sms():
    result = send_sms("9876543210", "Test alert")
    assert result["status"] == "SENT"
    assert result["channel"] == "sms"


def test_send_email():
    result = send_email("test@example.com", "Subject", "Body")
    assert result["status"] == "SENT"
    assert result["channel"] == "email"


def test_send_webhook():
    result = send_webhook("http://example.com/webhook", {"key": "value"})
    assert result["status"] == "SENT"
    assert result["channel"] == "webhook"


def test_dispatch_alert_multi_channel():
    recipients = {
        "phone": "9876543210",
        "email": "leo@example.com",
        "webhook_url": "http://example.com/hook",
    }
    results = dispatch_alert("Delhi-Zone-4", "HIGH", recipients)
    assert len(results) == 3
    assert all(r["status"] == "SENT" for r in results)