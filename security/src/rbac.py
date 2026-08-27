import jwt
from fastapi import Depends, HTTPException, Header

SECRET_KEY = "dev-secret-change-in-production"
ALGORITHM = "HS256"


def create_token(user_id: str, role: str) -> str:
    payload = {"sub": user_id, "role": role}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(authorization: str = Header(...)):
    try:
        scheme, token = authorization.split()
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing token")


def require_role(required_role: str):
    def checker(user: dict = Depends(get_current_user)):
        if user.get("role") != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Requires role: {required_role}",
            )
        return user
    return checker