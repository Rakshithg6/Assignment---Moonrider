from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class LinkPrecedenceEnum(enum.Enum):
    primary = "primary"
    secondary = "secondary"

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True, index=True)
    phoneNumber = Column(String, nullable=True)
    email = Column(String, nullable=True)
    linkedId = Column(Integer, ForeignKey('contacts.id'), nullable=True)
    linkPrecedence = Column(Enum(LinkPrecedenceEnum), nullable=False, default=LinkPrecedenceEnum.primary)
    createdAt = Column(DateTime(timezone=True), server_default=func.now())
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now())
    deletedAt = Column(DateTime(timezone=True), nullable=True)
