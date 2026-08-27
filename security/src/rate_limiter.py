import time
from collections import defaultdict
from fastapi import HTTPException, Request

WINDOW_SECONDS = 60
MAX_ATTEMPTS = 5

_attempts = defaultdict(list)


def check_rate_limit(request: Request):
    ip = request.client.host
    now = time.time()
    _attempts[ip] = [t for t in _attempts[ip] if now - t < WINDOW_SECONDS]

    if len(_attempts[ip]) >= MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Try again in {WINDOW_SECONDS} seconds.",
        )

    _attempts[ip].append(now)