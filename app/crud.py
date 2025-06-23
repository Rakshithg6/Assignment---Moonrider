from sqlalchemy.orm import Session
from .models import Contact, LinkPrecedenceEnum
from typing import Optional, List, Set

def get_contacts_by_email_or_phone(db: Session, email: Optional[str], phone: Optional[str]) -> List[Contact]:
    query = db.query(Contact)
    if email and phone:
        return query.filter((Contact.email == email) | (Contact.phoneNumber == phone)).all()
    elif email:
        return query.filter(Contact.email == email).all()
    elif phone:
        return query.filter(Contact.phoneNumber == phone).all()
    return []

def get_all_linked_contacts(db: Session, contacts: List[Contact]) -> List[Contact]:
    '''
    Given a set of contacts, traverse all linked contacts (directly or indirectly) and return the full group.
    '''
    seen: Set[int] = set()
    to_visit = [c.id for c in contacts]
    all_contacts = []
    while to_visit:
        cid = to_visit.pop()
        if cid in seen:
            continue
        seen.add(cid)
        group = db.query(Contact).filter((Contact.id == cid) | (Contact.linkedId == cid)).all()
        for c in group:
            if c.id not in seen:
                to_visit.append(c.id)
            if c.linkedId and c.linkedId not in seen:
                to_visit.append(c.linkedId)
            all_contacts.append(c)
    # Remove duplicates
    unique_contacts = {c.id: c for c in all_contacts}.values()
    return list(unique_contacts)

def get_primary_contact(contacts: List[Contact]) -> Contact:
    # Oldest contact in the group (by createdAt)
    return min(contacts, key=lambda c: c.createdAt)

def update_link_precedence(db: Session, contacts: List[Contact], primary: Contact):
    # Set only the oldest as primary, others as secondary
    for c in contacts:
        if c.id == primary.id:
            if c.linkPrecedence != LinkPrecedenceEnum.primary:
                c.linkPrecedence = LinkPrecedenceEnum.primary
                c.linkedId = None
        else:
            if c.linkPrecedence != LinkPrecedenceEnum.secondary or c.linkedId != primary.id:
                c.linkPrecedence = LinkPrecedenceEnum.secondary
                c.linkedId = primary.id
        db.add(c)
    db.commit()

# create_contact remains unchanged

def create_contact(db: Session, email: Optional[str], phone: Optional[str], linkPrecedence=LinkPrecedenceEnum.primary, linkedId: Optional[int]=None) -> Contact:
    contact = Contact(email=email, phoneNumber=phone, linkPrecedence=linkPrecedence, linkedId=linkedId)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact
