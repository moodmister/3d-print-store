from flask_sqlalchemy import SQLAlchemy
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship, DeclarativeBase, MappedAsDataclass

class Base(DeclarativeBase, MappedAsDataclass):
  pass

db = SQLAlchemy()

class Material(Base):
    __tablename__ = "material"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    cost_per_gram: Mapped[int]


class Spool(Base):
    __tablename__ = "spool"

    id: Mapped[int] = mapped_column(primary_key=True)
    make: Mapped[str]
    material_id: Mapped[int] = mapped_column(ForeignKey("material.id"))
    material: Mapped["Material"] = relationship()
    color: Mapped[str]
    grams: Mapped[int]
    grams_left: Mapped[int]


class File(Base):
    __tablename__ = "file"

    id: Mapped[int] = mapped_column(primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("model.id"))
    model: Mapped["StlModel"] = relationship(back_populates="file")
    full_path: Mapped[str]


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="orders")

    models: Mapped[List["StlModel"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    estimated_cost: Mapped[int]
    real_cost: Mapped[int]
    shipping: Mapped[int]

    delivery_address_id: Mapped[int] = mapped_column(ForeignKey("address.id"))
    delivery_address: Mapped["Address"] = relationship()

    payment_gateway_id: Mapped[int] = mapped_column(ForeignKey("payment_gateway.id"))
    payment_gateway: Mapped["PaymentGateway"] = relationship()

    def __repr__(self) -> str:
        return f"Order(id={self.id}, user_email={self.user.email})"


class StlModel(Base):
    __tablename__ = "stl_model"

    id: Mapped[int] = mapped_column(primary_key=True)

    file_id: Mapped[int] = mapped_column(ForeignKey("file.id"))
    file: Mapped["File"] = relationship(back_populates="model")
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    order: Mapped["Order"] = relationship(back_populates="models")

    estimated_time: Mapped[int]
    estimated_cost: Mapped[int]

    def __repr__(self) -> str:
        return f"StlModel(id{self.id})"


class PaymentGateway(Base):
    __tablename__ = "payment_gateway"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    type: Mapped[str]


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str]
    postal_code: Mapped[str]
    address_line1: Mapped[str]
    address_line2: Mapped[str] = mapped_column(nullable=False)


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    orders: Mapped[List["Order"]] = relationship(back_populates="order")
    roles: Mapped[List["Role"]] = relationship("UserRole", back_populates="user")

    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def has_permission(self, permission):
        for user_role in self.roles:
            if permission in user_role.role.permissions.split(","):
                return True
        return False

    def __repr__(self) -> str:
        return f"User(id={self.id}, email={self.email})"


class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    permissions: Mapped[str]
    users: Mapped[List["User"]] = relationship("UserRole", back_populates="role")

    def __repr__(self) -> str:
        return f"Role(id={self.id}, name={self.name})"


class UserRole(Base):
    __tablename__ = "user_role"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("role.id"), primary_key=True)

    user: Mapped["User"] = relationship("User", back_populates="roles")
    role: Mapped["Role"] = relationship("Role", back_populates="users")
