from sqlalchemy import Column, BigInteger, Integer, PrimaryKeyConstraint, ForeignKey, String, Boolean, CheckConstraint, UniqueConstraint, Date
from sqlalchemy.orm import relationship

from datetime import date

from models.users_model import Base


class Marketplace(Base):
    __tablename__ = 'marketplace'

    listing_id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete = 'CASCADE'))
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete = 'CASCADE'))
    quantity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    days_since_posted = Column(Integer, default=0)

    item = relationship('Items', back_populates='marketplace')
    user = relationship('User', back_populates='marketplace')


class ShopDaily(Base):
    __tablename__ = 'shop_daily'

    id = Column(Integer, primary_key=True)
    shop_type = Column(String, nullable=False)

    item_id = Column(Integer, ForeignKey('items.item_id', ondelete='CASCADE'), nullable=False)
    price = Column(Integer, nullable=False)
    is_bonus = Column(Boolean, default=False)
    date = Column(Date, nullable=False, default=date.today)

    __table_args__ = (
        CheckConstraint("shop_type IN ('sell', 'buyback')", name='shop_type_valid'),
        UniqueConstraint('date', 'item_id', name='unique_daily_item_no_dupe'),
    )

    item = relationship('Items')