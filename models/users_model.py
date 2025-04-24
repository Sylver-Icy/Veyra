from sqlalchemy import Column, BigInteger, String, Integer, SmallInteger, TIMESTAMP
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(40), nullable=False)
    exp = Column(Integer, default=0)
    level = Column(SmallInteger, default=1)
    joined = Column(TIMESTAMP, nullable=False)