from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    price_selector = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    history = relationship("PriceHistory", back_populates="product")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    change_detected = Column(Boolean, default=False)

    product = relationship("Product", back_populates="history")