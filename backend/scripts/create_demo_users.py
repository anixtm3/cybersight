"""
scripts/create_demo_users.py

Creates the 3 demo role accounts needed for the Day 1 checkpoint
("three demo roles created and authenticating"). Passwords are
hashed with the same passlib/bcrypt scheme auth.py/auth_core.py use
for verification.

REQUIRES: migration_day1_fixes.sql already run (adds users.bank_name).

Run from backend/:
    python -m scripts.create_demo_users
"""

from app.database import SessionLocal
from app.models.complaint import User
from app.auth_core import hash_password

# Change these passwords before a real demo if this ever leaves a
# throwaway local Ganache/Postgres setup.
DEMO_USERS = [
    {"username": "i4c_admin", "password": "Admin@123", "role": "admin",
     "jurisdiction_district": None, "bank_name": None},
    {"username": "officer_delhi", "password": "Officer@123", "role": "cyber_cell_officer",
     "jurisdiction_district": "New Delhi", "bank_name": None},
    {"username": "nodal_hdfc", "password": "Nodal@123", "role": "bank_nodal_officer",
     "jurisdiction_district": None, "bank_name": "HDFC"},
]


def create_demo_users():
    db = SessionLocal()
    try:
        for u in DEMO_USERS:
            existing = db.query(User).filter(User.username == u["username"]).first()
            if existing:
                print(f"Skipping {u['username']} — already exists")
                continue

            user = User(
                username=u["username"],
                password_hash=hash_password(u["password"]),
                role=u["role"],
                jurisdiction_district=u["jurisdiction_district"],
                bank_name=u["bank_name"],
            )
            db.add(user)
            print(f"Created {u['username']} ({u['role']}) — password: {u['password']}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_users()