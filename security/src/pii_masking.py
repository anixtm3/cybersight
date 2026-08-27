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


if __name__ == "__main__":
    print(mask_phone("9876543210"))
    print(mask_email("kanav.agarwal@gmail.com"))
    print(mask_account_number("123456789012"))