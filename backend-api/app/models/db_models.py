from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel, func
from sqlalchemy import Column, CheckConstraint, Numeric, Integer

class Products(SQLModel, table=True):
    __table_args__ = {"schema": "b2b"}
    
    product_id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(nullable=False)
    name: str = Field(nullable=False)
    description: str
    category: str
    
    u_price: Decimal = Field(
        sa_column=Column(
            Numeric(precision=10, scale=2), 
            CheckConstraint("u_price >= 0"), 
            nullable=False,
            default=0
        )
    )
    
    stock_qnt: int = Field(
        default=0, 
        nullable=False, 
        sa_column_args=[CheckConstraint("stock_qnt >= 0")]
    )

    order_items: List["OrderItem"] = Relationship(back_populates="product")

class Users(SQLModel, table=True):
    __table_args__ = {"schema": "b2b"}
    
    user_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(nullable=False)
    surname: str = Field(nullable=False)
    email: str = Field(nullable=False, unique=True)

    orders: List["Orders"] = Relationship(back_populates="user")

class Orders(SQLModel, table=True):
    __table_args__ = {"schema": "b2b"}
    
    order_id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(nullable=False, foreign_key="b2b.users.user_id")
    
    placed_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, 
        nullable=False
    )
    resolved_at: Optional[datetime] = Field(default=None)

    items: List["OrderItem"] = Relationship(back_populates="order")
    user: "Users" = Relationship(back_populates="orders")

class OrderItem(SQLModel, table=True):
    __table_args__ = {"schema": "b2b"}
    
    id: Optional[int] = Field(default=None, primary_key=True)

    product_id: int = Field(nullable=False, foreign_key="b2b.products.product_id")
    order_id: int = Field(nullable=False, foreign_key="b2b.orders.order_id")
    

    qnt: int = Field(
        sa_column=Column(
            Integer, 
            CheckConstraint("qnt > 0"), 
            nullable=False
        )
    )
    
    u_price: Decimal = Field(
        sa_column=Column(
            Numeric(precision=10, scale=2), 
            CheckConstraint("u_price >= 0"), 
            nullable=False
        )
    )

    order: "Orders" = Relationship(back_populates="items")
    product: "Products" = Relationship(back_populates="order_items")