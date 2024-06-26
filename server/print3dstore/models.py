from enum import StrEnum
import json
from flask_sqlalchemy import SQLAlchemy
from typing import List, Optional
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship, DeclarativeBase, MappedAsDataclass

db = SQLAlchemy()

class Printer(db.Model):
    __tablename__ = "printer"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    config_file: Mapped[str|None]


class Material(db.Model):
    __tablename__ = "material"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    cost_per_gram: Mapped[int]

    def __repr__(self) -> str:
        return self.name


class Spool(db.Model):
    __tablename__ = "spool"

    id: Mapped[int] = mapped_column(primary_key=True)
    make: Mapped[str]
    material_id: Mapped[int] = mapped_column(ForeignKey("material.id"))
    material: Mapped["Material"] = relationship(foreign_keys=material_id)
    color: Mapped[str]
    grams: Mapped[int]
    grams_left: Mapped[int]


class File(db.Model):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(primary_key=True)
    stl_model: Mapped["StlModel"] = relationship(back_populates="file")
    full_path: Mapped[str]


class Order(db.Model):
    class Status(StrEnum):
        QUEUED = "queued"
        IN_PROGRESS = "in progress"
        SHIPPED = "shipped"
        FINISHED = "finished"
        CANCELLED = "cancelled"

    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="orders", foreign_keys=user_id)

    stl_models: Mapped[List["StlModel"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    estimated_cost: Mapped[int|None]
    real_cost: Mapped[int|None]
    shipping_cost: Mapped[int|None]
    status: Mapped[str|None] = mapped_column(default=Status.QUEUED)

    city: Mapped[str|None]
    postal_code: Mapped[str|None]
    address_line1: Mapped[str|None]
    address_line2: Mapped[str|None]
    phone: Mapped[str|None]

    payment_gateway_id: Mapped[int] = mapped_column(ForeignKey("payment_gateway.id"))
    payment_gateway: Mapped["PaymentGateway"] = relationship(foreign_keys=payment_gateway_id)

    def __repr__(self) -> str:
        return f"Order(id={self.id}, user_email={self.user.email})"


class StlModel(db.Model):
    __tablename__ = "stl_model"

    id: Mapped[int] = mapped_column(primary_key=True)

    file_id: Mapped[int] = mapped_column(ForeignKey("file.id"))
    file: Mapped["File"] = relationship(foreign_keys=file_id, back_populates="stl_model")
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    order: Mapped["Order"] = relationship(back_populates="stl_models", foreign_keys=order_id)

    color: Mapped[str|None]
    material_id: Mapped[int] = mapped_column(ForeignKey("material.id"))
    material: Mapped["Material"] = relationship(foreign_keys=material_id)

    estimated_time: Mapped[int|None]
    estimated_cost: Mapped[int|None]

    errors: Mapped[str|None]

    def __repr__(self) -> str:
        return f"StlModel(id{self.file.full_path.split('/')[-1]})"


class PaymentGateway(db.Model):
    __tablename__ = "payment_gateway"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str]

    def __repr__(self) -> str:
        return f"{self.name} ({self.type})"


class User(db.Model):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]  = mapped_column(String)
    orders: Mapped[Optional[List["Order"]]] = relationship(back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[List["Role"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    city: Mapped[str|None]
    postal_code: Mapped[str|None]
    address_line1: Mapped[str|None]
    address_line2: Mapped[str|None]

    phone: Mapped[str|None]

    def has_permission(self, permission):
        for user_role in self.roles:
            permissions_json = json.loads(user_role.role.permissions)
            if permissions_json.get(permission):
                return True
        return False

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email})"


class Role(db.Model):
    all_permissions = {
        "Superuser": "superuser",
        "Order": {
            "read": "read_orders",
            "write": "write_orders"
        },
        "User": {
            "read": "read_users",
            "write": "write_users"
        },
        "Role": {
            "read": "read_roles",
            "write": "write_roles"
        },
        "Material": {
            "read": "read_materials",
            "write": "write_materials"
        },
        "File": {
            "read": "read_files",
            "write": "write_files"
        },
        "Stl Model": {
            "read": "read_stl_models",
            "write": "write_stl_models"
        },
        "Spool": {
            "read": "read_spools",
            "write": "write_spools"
        },
        "Payment Gateway": {
            "read": "read_payment_gateways",
            "write": "write_payment_gateways"
        },
        "Printer": {
            "read": "read_printers",
            "write": "write_printers"
        }
    }

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    permissions: Mapped[str]
    users: Mapped[List["User"]] = relationship("UserRole", back_populates="role")

    def __repr__(self) -> str:
        return f"Role(id={self.id}, name={self.name})"


class UserRole(db.Model):
    __tablename__ = "user_role"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="roles")
    role: Mapped["Role"] = relationship("Role", back_populates="users")

    def __repr__(self) -> str:
        return self.role.name
