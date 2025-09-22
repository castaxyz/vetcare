"""
EXPLICACIÓN: Modelos SQLAlchemy que mapean las entidades de dominio a tablas de BD.
Estos modelos NO contienen lógica de negocio, solo mapeo objeto-relacional.
Son la representación técnica de nuestras entidades de dominio.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Float, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()

# Enums para mantener consistencia con el dominio
class UserRoleEnum(enum.Enum):
    ADMIN = "admin"
    VETERINARIAN = "veterinarian"
    RECEPTIONIST = "receptionist"
    ASSISTANT = "assistant"

class PetSpeciesEnum(enum.Enum):
    DOG = "dog"
    CAT = "cat"
    BIRD = "bird"
    RABBIT = "rabbit"
    HAMSTER = "hamster"
    OTHER = "other"

class PetGenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    UNKNOWN = "unknown"

class AppointmentStatusEnum(enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"

class AppointmentTypeEnum(enum.Enum):
    CONSULTATION = "consultation"
    VACCINATION = "vaccination"
    SURGERY = "surgery"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"
    GROOMING = "grooming"

class UserModel(Base):
    """
    Modelo SQLAlchemy para usuarios del sistema.
    Mapea la entidad User a la tabla 'users'.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRoleEnum), nullable=False, default=UserRoleEnum.RECEPTIONIST, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    created_appointments = relationship("AppointmentModel", back_populates="creator", foreign_keys="AppointmentModel.created_by")
    assigned_appointments = relationship("AppointmentModel", back_populates="veterinarian", foreign_keys="AppointmentModel.veterinarian_id")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role.value}')>"

class ClientModel(Base):
    """
    Modelo SQLAlchemy para clientes (propietarios de mascotas).
    Mapea la entidad Client a la tabla 'clients'.
    """
    __tablename__ = 'clients'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=True, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    identification_number = Column(String(20), nullable=True, unique=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    pets = relationship("PetModel", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.first_name} {self.last_name}')>"

class PetModel(Base):
    """
    Modelo SQLAlchemy para mascotas.
    Mapea la entidad Pet a la tabla 'pets'.
    """
    __tablename__ = 'pets'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    species = Column(Enum(PetSpeciesEnum), nullable=False, default=PetSpeciesEnum.OTHER, index=True)
    breed = Column(String(50), nullable=True)
    birth_date = Column(Date, nullable=True)
    gender = Column(Enum(PetGenderEnum), nullable=False, default=PetGenderEnum.UNKNOWN)
    color = Column(String(30), nullable=True)
    weight = Column(Float, nullable=True)
    microchip_number = Column(String(20), nullable=True, unique=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    owner = relationship("ClientModel", back_populates="pets")
    appointments = relationship("AppointmentModel", back_populates="pet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Pet(id={self.id}, name='{self.name}', species='{self.species.value}')>"

class AppointmentModel(Base):
    """
    Modelo SQLAlchemy para citas veterinarias.
    Mapea la entidad Appointment a la tabla 'appointments'.
    """
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False, index=True)
    veterinarian_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    appointment_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=30)
    appointment_type = Column(Enum(AppointmentTypeEnum), nullable=False, index=True)
    status = Column(Enum(AppointmentStatusEnum), nullable=False, default=AppointmentStatusEnum.SCHEDULED, index=True)
    reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relaciones
    pet = relationship("PetModel", back_populates="appointments")
    veterinarian = relationship("UserModel", back_populates="assigned_appointments", foreign_keys=[veterinarian_id])
    creator = relationship("UserModel", back_populates="created_appointments", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, pet_id={self.pet_id}, date='{self.appointment_date}', status='{self.status.value}')>"

# Índices adicionales para optimización
from sqlalchemy import Index

# Índices compuestos para consultas frecuentes
Index('idx_appointments_date_status', AppointmentModel.appointment_date, AppointmentModel.status)
Index('idx_appointments_vet_date', AppointmentModel.veterinarian_id, AppointmentModel.appointment_date)
Index('idx_pets_client_active', PetModel.client_id, PetModel.is_active)