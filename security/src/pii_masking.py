def mask_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) <= 4:
        return "*" * len(digits)
    return "X" * (len(digits) - 4) + digits[-4:]


def mask_email(email: str) -> str:
    if "@" not in email:
        return "*" * len(email)
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = local[0] + "*"
    else:
        masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def mask_account_number(account: str) -> str:
    chars = "".join(c for c in account if c.isalnum())
    if len(chars) <= 4:
        return "*" * len(chars)
    return "*" * (len(chars) - 4) + chars[-4:]


def mask_aadhaar(aadhaar: str) -> str:
    digits = "".join(c for c in aadhaar if c.isdigit())
    if len(digits) != 12:
        return "*" * len(digits)
    return "XXXX XXXX " + digits[-4:]


def mask_pan(pan: str) -> str:
    pan = pan.strip().upper()
    if len(pan) != 10:
        return "*" * len(pan)
    return pan[:2] + "X" * 6 + pan[-2:]


def mask_address(address: str) -> str:
    parts = address.split(",")
    if len(parts) <= 1:
        return "*" * len(address)
    return "*** " + parts[-1].strip()