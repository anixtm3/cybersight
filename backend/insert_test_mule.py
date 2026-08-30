from app.database import SessionLocal
from app.models.complaint import MuleAccount
from datetime import datetime

db = SessionLocal()
test_mule = MuleAccount(
    account_number='1234567890123456',
    account_holder_name='Test Holder',
    bank_name='Test Bank',
    risk_score=0.85,
    is_red_flagged=True,
    red_flagged_at=datetime.utcnow()
)
db.add(test_mule)
db.commit()
print('Inserted successfully')
db.close()
