from sqlalchemy import Column, BigInteger, Integer, PrimaryKeyConstraint, ForeignKey
from sqlalchemy.orm import relationship
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