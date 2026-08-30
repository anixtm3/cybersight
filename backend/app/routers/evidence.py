import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_core import get_current_user
from app.models.complaint import Complaint, CaseNote, ActionLog, AuditLog, User
from app.schemas.complaint import (
    CaseNoteCreate,
    CaseNoteResponse,
    ActionLogCreate,
    ActionLogResponse,
)

router = APIRouter(prefix="/api/complaints", tags=["evidence"])


def _get_complaint_or_404(complaint_id: str, db: Session) -> Complaint:
    complaint = db.query(Complaint).filter(Complaint.complaint_id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


def _log_audit(db: Session, admin_id: int, action: str, target_id: str, request: Request):
    # log_id has no DB-side default anymore — must set it explicitly here.
    db.add(
        AuditLog(
            log_id=uuid.uuid4(),
            admin_id=admin_id,
            action=action,
            target_id=target_id,
            ip_address=request.client.host if request.client else None,
            status="SUCCESS",
        )
    )
    db.commit()


# ─── CASE NOTES ──────────────────────────────────────────

@router.post("/{complaint_id}/notes", response_model=CaseNoteResponse)
def add_case_note(
    complaint_id: str,
    note_data: CaseNoteCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_complaint_or_404(complaint_id, db)

    note = CaseNote(
        complaint_id=complaint_id,
        officer_id=current_user.id,  # from the token, never from the client
        note=note_data.note,
    )
    db.add(note)
    db.commit()
    db.refresh(note)

    _log_audit(db, current_user.id, "case_note_added", complaint_id, request)

    return note


@router.get("/{complaint_id}/notes", response_model=List[CaseNoteResponse])
def list_case_notes(
    complaint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_complaint_or_404(complaint_id, db)
    return (
        db.query(CaseNote)
        .filter(CaseNote.complaint_id == complaint_id)
        .order_by(CaseNote.created_at.desc())
        .all()
    )


# ─── ACTION LOG ──────────────────────────────────────────

@router.post("/{complaint_id}/actions", response_model=ActionLogResponse)
def add_action_log(
    complaint_id: str,
    action_data: ActionLogCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_complaint_or_404(complaint_id, db)

    action = ActionLog(
        complaint_id=complaint_id,
        officer_id=current_user.id,
        action_type=action_data.action_type,
        details=action_data.details,
    )
    db.add(action)
    db.commit()
    db.refresh(action)

    _log_audit(db, current_user.id, f"action_log:{action_data.action_type}", complaint_id, request)

    return action


@router.get("/{complaint_id}/actions", response_model=List[ActionLogResponse])
def list_action_log(
    complaint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_complaint_or_404(complaint_id, db)
    return (
        db.query(ActionLog)
        .filter(ActionLog.complaint_id == complaint_id)
        .order_by(ActionLog.created_at.desc())
        .all()
    )