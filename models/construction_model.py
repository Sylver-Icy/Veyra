from sqlalchemy import Column, BigInteger, Integer, Boolean, TIMESTAMP, ForeignKey, Text, func
from sqlalchemy.orm import relationship

from models.users_model import Base

class UserTree(Base):
    __tablename__ = 'user_trees'

    tree_id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    exp = Column(Integer, nullable=False, default=0)
    lvl = Column(Integer, nullable=False, default=1)

    last_pruned = Column(TIMESTAMP, nullable=True)
    planted_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    is_alive = Column(Boolean, nullable=False, default=True)

    user = relationship("User")

class Sylphs(Base):
    __tablename__ = 'sylphs'

    sylph_id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(Text, nullable=False)

    born_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    user_id = Column(
        BigInteger,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    tree_id = Column(
        Integer,
        ForeignKey('user_trees.tree_id', ondelete='SET NULL'),
        nullable=True
    )

    assigned_construction_id = Column(Integer, nullable=True)
    assigned_at = Column(TIMESTAMP, nullable=True)

    happiness = Column(Integer, nullable=False, default=100)
    food = Column(Integer, nullable=False, default=100)

    is_dead = Column(Boolean, nullable=False, default=False)

    user = relationship("User")
    tree = relationship("UserTree")