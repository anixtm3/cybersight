# reset_passwords.py — one-time script, delete after use
from app.database import SessionLocal
from app.models.complaint import User
from app.auth_core import hash_password

NEW_PASSWORD = "Test@123"

db = SessionLocal()
usernames = ["admin", "i4c_admin", "nodal_hdfc", "officer_delhi"]

for uname in usernames:
    user = db.query(User).filter(User.username == uname).first()
    if user:
        user.password_hash = hash_password(NEW_PASSWORD)
        print(f"Reset password for: {uname} (role: {user.role})")
    else:
        print(f"NOT FOUND: {uname}")

db.commit()
db.close()
print("Done.")