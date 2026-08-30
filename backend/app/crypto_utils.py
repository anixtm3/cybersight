"""
app/crypto_utils.py

Single source of truth for hashing account numbers before any
blockchain interaction (read or write). Both the read-side (checking
if an account is blacklisted) and the write-side (Aniket's flag
endpoint) MUST call this same function, or hashes will never match
and every check will silently come back "not blacklisted."

Uses a fixed secret salt (a "pepper") rather than a per-record random
salt — deliberately, because we need to re-derive the same hash from
the same account number later to look it up. A per-record random salt
would make that impossible. Keep ACCOUNT_HASH_SALT secret (env var,
not committed) — that's what protects against rainbow-table reversal.
"""

import hashlib
import os

_ACCOUNT_HASH_SALT = os.environ["ACCOUNT_HASH_SALT"]


def hash_account_number(account_number: str) -> str:
    if not account_number:
        raise ValueError("account_number is required for hashing")
    return hashlib.sha256((_ACCOUNT_HASH_SALT + account_number).encode()).hexdigest()