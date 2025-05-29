from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, BigInteger, String, Integer
from sqlalchemy.orm import relationship
from models.users_model import Base



class Inventory(Base):
    __tablename__ = 'inventory'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'item_id'),
    )
    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'))
    item_id = Column(Integer, ForeignKey('items.item_id', ondelete='CASCADE'))
    item_quantity = Column(Integer, default=1)
    item_durability = Column(Integer)

    item = relationship('Items', back_populates='inventory')
    user = relationship('User', back_populates='inventory')
class Items(Base):
    __tablename__ = 'items'

    item_id = Column(Integer, autoincrement=True, primary_key=True)
    item_name = Column(String, unique=True, nullable=False)
    item_description = Column(String, nullable=False)
    item_rarity = Column(String, nullable=False)
    item_icon = Column(String, nullable=True)
    item_durability = Column(Integer, nullable=True)

    inventory = relationship('Inventory', back_populates='item')
    


