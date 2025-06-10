from sqlalchemy import Column, ForeignKey, BigInteger, String, Integer, SmallInteger, TIMESTAMP 
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(40), nullable=False)
    exp = Column(Integer, default=0)
    level = Column(SmallInteger, default=1)
    joined = Column(TIMESTAMP, nullable=False)

    wallet = relationship('Wallet', back_populates='user', uselist=False, cascade='all, delete')
    inventory = relationship('Inventory', back_populates='user', cascade='all, delete')

class Wallet(Base):
    __tablename__ = 'wallet'

    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    gold = Column(Integer, default=0)

    user = relationship("User", back_populates="wallet")
