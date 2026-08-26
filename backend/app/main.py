from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, func
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime, timedelta
import hashlib
import os

from app.database import engine, SessionLocal
from app.models.complaint import RevokedToken, Complaint
from app.routers import complaints, predict, auth, ingest, heatmap, websocket, reports, mule

from app.rate_limit import limiter

app = FastAPI(
    title="Cybercrime Prediction API",
    description="SIH PS 77 backend",
    version="0.2.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

PUBLIC_ROUTES = [
    "/",
    "/health",
    "/health/db",
    "/api/auth/login",
    "/api/dashboard/stats",
    "/docs",
    "/openapi.json",
    "/redoc",
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.middleware("http")
async def check_revoked_token(request: Request, call_next):
    # ✅ OPTIONS preflight requests are ALWAYS exempt from JWT auth,
    # for every route, with no exceptions. Browsers never attach an
    # Authorization header on a CORS preflight, so checking it here
    # would always fail and block CORSMiddleware from ever attaching
    # the proper Access-Control-Allow-Origin headers. This check must
    # stay first, before PUBLIC_ROUTES, so it covers ALL routes
    # (including /api/complaints, /api/heatmap, and any future route)
    # without needing to list each one in PUBLIC_ROUTES.
    if request.method == "OPTIONS":
        return await call_next(request)

    if request.url.path in PUBLIC_ROUTES:
        return await call_next(request)

    if request.url.path.startswith("/ws"):
        return await call_next(request)

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return JSONResponse(
            status_code=401,
            content={"detail": "Authorization header missing"}
        )

    try:
        token = auth_header.replace("Bearer ", "")
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        db = SessionLocal()
        revoked = db.query(RevokedToken).filter(
            RevokedToken.token_hash == token_hash
        ).first()
        db.close()

        if revoked:
            return JSONResponse(
                status_code=401,
                content={"detail": "Token revoked"}
            )

    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid token"}
        )

    return await call_next(request)


app.include_router(complaints.router)
app.include_router(predict.router)
app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(heatmap.router)
app.include_router(websocket.router)
app.include_router(reports.router)
app.include_router(mule.router)


@app.get("/")
def root():
    return {
        "message": "Cybercrime Prediction API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as exc:
        return {"database": "error", "detail": str(exc)}


# ✅ DASHBOARD STATS
@app.get("/api/dashboard/stats")
def dashboard_stats(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)
    two_weeks_ago = now - timedelta(days=14)

    high = db.query(func.count(Complaint.id)).filter(Complaint.alert_level == "HIGH").scalar() or 0
    medium = db.query(func.count(Complaint.id)).filter(Complaint.alert_level == "MEDIUM").scalar() or 0
    low = db.query(func.count(Complaint.id)).filter(Complaint.alert_level == "LOW").scalar() or 0

    this_week = db.query(func.count(Complaint.id)).filter(Complaint.created_at >= week_ago).scalar() or 0
    prev_week = db.query(func.count(Complaint.id)).filter(
        Complaint.created_at >= two_weeks_ago,
        Complaint.created_at < week_ago
    ).scalar() or 0

    avg_high = round(high / 7, 2)

    if prev_week > 0:
        trend = round(((this_week - prev_week) / prev_week) * 100, 2)
    else:
        trend = 0.0

    active_zones = db.query(func.count(func.distinct(Complaint.victim_district))).filter(
        Complaint.alert_level == "HIGH"
    ).scalar() or 0

    return {
        "high_alerts": high,
        "medium_alerts": medium,
        "low_alerts": low,
        "total_this_week": this_week,
        "avg_high_per_day": avg_high,
        "week_trend_percent": trend,
        "active_zones": active_zones,
    }