from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from backend.app.db.database import get_db
from backend.app.db.models import UserModel
from backend.app.auth.token import get_current_user
from backend.app.tickets.classifier import ITIntentClassifier
from backend.app.tickets.service import TicketService

router = APIRouter(prefix="/api/tickets", tags=["IT Helpdesk & Ticketing"])

@router.post("/classify")
def classify_ticket_intent(text: str = Body(..., embed=True)):
    result = ITIntentClassifier.classify(text)
    return result

@router.post("")
def create_ticket(
    payload: Dict[str, Any] = Body(...),
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    confirmed = payload.get("confirmed", False)
    if not confirmed:
        raise HTTPException(
            status_code=400,
            detail="Ticket creation cancelled: User must explicitly confirm ticket submission."
        )

    ticket = TicketService.create_ticket(
        user=user,
        ticket_data=payload,
        confirmed=confirmed,
        db=db
    )

    return {
        "status": "ticket_created",
        "ticket_number": ticket.ticket_number,
        "category": ticket.category,
        "priority": ticket.priority,
        "assigned_team": ticket.assigned_team,
        "created_at": ticket.created_at.isoformat()
    }

@router.get("")
def list_my_tickets(
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tickets = TicketService.get_user_tickets(user.id, db)
    return [
        {
            "ticket_number": t.ticket_number,
            "category": t.category,
            "summary": t.summary,
            "priority": t.priority,
            "status": t.status,
            "assigned_team": t.assigned_team,
            "created_at": t.created_at.isoformat() if t.created_at else None
        }
        for t in tickets
    ]

@router.get("/{ticket_number}")
def get_ticket(
    ticket_number: str,
    user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = TicketService.get_ticket_by_number(ticket_number, db)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    if ticket.user_id != user.id and user.role not in {"it_support", "it_admin", "system_admin"}:
        raise HTTPException(status_code=403, detail="Unauthorized to view this ticket.")

    return {
        "ticket_number": ticket.ticket_number,
        "user_email": ticket.user_email,
        "category": ticket.category,
        "summary": ticket.summary,
        "description": ticket.description,
        "priority": ticket.priority,
        "device_type": ticket.device_type,
        "operating_system": ticket.operating_system,
        "status": ticket.status,
        "assigned_team": ticket.assigned_team,
        "created_at": ticket.created_at.isoformat() if ticket.created_at else None
    }
