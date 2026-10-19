import random
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.app.db.models import TicketModel, UserModel

class TicketService:
    @staticmethod
    def create_ticket(
        user: UserModel,
        ticket_data: Dict[str, Any],
        confirmed: bool,
        db: Session
    ) -> TicketModel:
        """
        Creates an internal IT support ticket.
        MANDATORY RULE: Requires explicit confirmed=True from the user.
        """
        if not confirmed:
            raise HTTPException(
                status_code=400,
                detail="Ticket creation cancelled: Explicit user confirmation is strictly required before submitting IT tickets."
            )

        ticket_number = f"TICK-{int(time.time() % 1000000):06d}"
        priority = ticket_data.get("priority", "medium").lower()

        assigned_team = "Information Security (ISOC)" if ticket_data.get("security_incident") or priority == "critical" else "IT Support L1"

        ticket = TicketModel(
            ticket_number=ticket_number,
            user_id=user.id,
            user_email=user.email,
            category=ticket_data.get("category", "General IT"),
            summary=ticket_data.get("summary", "IT Support Request"),
            description=ticket_data.get("description", "No description provided"),
            priority=priority,
            device_type=ticket_data.get("device_type", "Corporate Workstation"),
            operating_system=ticket_data.get("operating_system", "Windows/macOS"),
            location=ticket_data.get("location", "Remote/Office"),
            error_message=ticket_data.get("error_message"),
            business_impact=ticket_data.get("business_impact", "Standard"),
            status="open",
            assigned_team=assigned_team
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    @staticmethod
    def get_user_tickets(user_id: str, db: Session) -> List[TicketModel]:
        return db.query(TicketModel).filter(TicketModel.user_id == user_id).order_by(TicketModel.created_at.desc()).all()

    @staticmethod
    def get_ticket_by_number(ticket_number: str, db: Session) -> Optional[TicketModel]:
        return db.query(TicketModel).filter(TicketModel.ticket_number == ticket_number).first()
