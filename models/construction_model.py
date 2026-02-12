from sqlalchemy import Column, BigInteger, Integer, Boolean, TIMESTAMP, ForeignKey, func
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