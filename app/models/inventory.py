from sqlalchemy import Column, String, Integer, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base
import uuid
from datetime import datetime


class Device(Base):
    """Modello per i dispositivi dell'Ufficio Polizia Locale (bodycam, fototrappole, radio, etc.)"""
    __tablename__ = "devices"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)  # Nome del dispositivo
    type = Column(String, nullable=False, index=True)  # Tipo (bodycam, fototrappola, radio, etc.)
    brand = Column(String, nullable=True)  # Marca
    model = Column(String, nullable=True)  # Modello
    serial_number = Column(String, nullable=True, unique=True)  # Numero seriale
    status = Column(String, nullable=False, default="disponibile")  # disponibile, in uso, in manutenzione, fuori servizio
    purchase_date = Column(DateTime, nullable=True)  # Data acquisto
    warranty_expiry = Column(DateTime, nullable=True)  # Scadenza garanzia
    location = Column(String, nullable=True)  # Ubicazione
    notes = Column(Text, nullable=True)  # Note aggiuntive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TemporarySignage(Base):
    """Modello per la segnaletica temporanea (cartelli temporanei con quantità)"""
    __tablename__ = "temporary_signage"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)  # Nome del cartello
    type = Column(String, nullable=False, index=True)  # Tipo (divieto sosta, transito, direzione obbligatoria, etc.)
    description = Column(Text, nullable=True)  # Descrizione dettagliata
    quantity = Column(Integer, nullable=False, default=0)  # Quantità disponibile
    min_quantity = Column(Integer, nullable=False, default=0)  # Quantità minima di sicurezza
    location = Column(String, nullable=True)  # Ubicazione magazzino
    size = Column(String, nullable=True)  # Dimensioni
    material = Column(String, nullable=True)  # Materiale
    is_active = Column(Boolean, default=True)  # Attivo/Disattivo
    notes = Column(Text, nullable=True)  # Note aggiuntive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VerticalSignage(Base):
    """Modello per la segnaletica verticale (cartelli permanenti, targhe viarie, etc.)"""
    __tablename__ = "vertical_signage"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, index=True)  # Nome del cartello
    type = Column(String, nullable=False, index=True)  # Tipo (divieto sosta, transito, targa viaria, etc.)
    code = Column(String, nullable=True, index=True)  # Codice identificativo
    description = Column(Text, nullable=True)  # Descrizione dettagliata
    quantity = Column(Integer, nullable=False, default=0)  # Quantità disponibile
    min_quantity = Column(Integer, nullable=False, default=0)  # Quantità minima di sicurezza
    location = Column(String, nullable=True)  # Ubicazione magazzino
    size = Column(String, nullable=True)  # Dimensioni
    material = Column(String, nullable=True)  # Materiale
    street_name = Column(String, nullable=True)  # Nome via (per targhe viarie)
    installation_date = Column(DateTime, nullable=True)  # Data installazione
    is_active = Column(Boolean, default=True)  # Attivo/Disattivo
    notes = Column(Text, nullable=True)  # Note aggiuntive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)