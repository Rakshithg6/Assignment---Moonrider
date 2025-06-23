from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, init_db
from .schemas import IdentifyRequest, IdentifyResponse
from .crud import get_contacts_by_email_or_phone, create_contact, get_all_linked_contacts, get_primary_contact, update_link_precedence
from .models import Contact, LinkPrecedenceEnum
from typing import List

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/identify", response_model=IdentifyResponse)
def identify(payload: IdentifyRequest, db: Session = Depends(get_db)):
    email = payload.email
    phone = payload.phoneNumber
    if not email and not phone:
        raise HTTPException(status_code=400, detail="Email or phoneNumber required.")
    
    # Step 1: Find all contacts that match email or phone
    initial_contacts = get_contacts_by_email_or_phone(db, email, phone)
    if not initial_contacts:
        # No match: create new primary
        new_contact = create_contact(db, email, phone, LinkPrecedenceEnum.primary)
        return IdentifyResponse(
            primaryContactId=new_contact.id,
            emails=[email] if email else [],
            phoneNumbers=[phone] if phone else [],
            secondaryContactIds=[]
        )
    
    # Step 2: Traverse all linked contacts (full group)
    group_contacts = get_all_linked_contacts(db, initial_contacts)
    primary = get_primary_contact(group_contacts)
    
    # Step 3: If new info, create secondary
    emails_set = set(c.email for c in group_contacts if c.email)
    phones_set = set(c.phoneNumber for c in group_contacts if c.phoneNumber)
    new_secondary = None
    needs_new_secondary = False
    if (email and email not in emails_set) or (phone and phone not in phones_set):
        # New info introduced, create secondary linked to primary
        new_secondary = create_contact(db, email, phone, LinkPrecedenceEnum.secondary, linkedId=primary.id)
        group_contacts.append(new_secondary)
        if email:
            emails_set.add(email)
        if phone:
            phones_set.add(phone)
    
    # Step 4: Update link precedence in group
    update_link_precedence(db, group_contacts, primary)
    
    # Step 5: Prepare response
    all_emails = sorted(emails_set)
    all_phones = sorted(phones_set)
    secondary_ids = sorted([c.id for c in group_contacts if c.linkPrecedence == LinkPrecedenceEnum.secondary and c.deletedAt is None])
    return IdentifyResponse(
        primaryContactId=primary.id,
        emails=all_emails,
        phoneNumbers=all_phones,
        secondaryContactIds=secondary_ids
    )
