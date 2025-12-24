from sqlalchemy import Column, ForeignKey, BigInteger, String, Integer, SmallInteger, TIMESTAMP, Boolean, PrimaryKeyConstraint, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True)
    user_name = Column(String(40), nullable=False)
    exp = Column(Integer, default=0)
    level = Column(SmallInteger, default=1)
    joined = Column(TIMESTAMP, nullable=False)
    starter_given = Column(Boolean, nullable=False, default=False)
    energy = Column(Integer, default=0)
    tutorial_state = Column(Integer, default=0)
    campaign_stage = Column(Integer, default=0)

    wallet = relationship('Wallet', back_populates='user', uselist=False, cascade='all, delete')
    inventory = relationship('Inventory', back_populates='user', cascade='all, delete')
    marketplace = relationship('Marketplace', back_populates = 'user')
    upgrades = relationship("Upgrades", back_populates="user")

class Wallet(Base):
    __tablename__ = 'wallet'

    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    gold = Column(Integer, default=0)

    user = relationship("User", back_populates="wallet")

class Quests(Base):
    __tablename__ = 'quests'

    user_id = Column(BigInteger, primary_key=True)
    delivery_items = Column(JSONB, default=list)
    reward = Column(Integer, default=0)
    limit = Column(Integer, default=0)
    skips = Column(Integer, default =0)
    streak = Column(Integer, default=0)

class Daily(Base):
    __tablename__ = 'daily'

    user_id = Column(BigInteger, primary_key=True)
    number_game = Column(Boolean, default=False)

class LotteryEntries(Base):
    __tablename__ = 'lottery_entries'

    user_id = Column(BigInteger, primary_key=True)
    tickets = Column(JSONB, default=list)
    ticket_price = Column(Integer, default=10)

class Friendship(Base):
    __tablename__ = 'friendship'

    user_id = Column(BigInteger, primary_key=True)
    friendship_exp = Column(Integer, default=0)
    daily_exp = Column(Integer, default=0)

class Upgrades(Base):
    __tablename__ = 'user_upgrades'
    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'upgrade_name'),
    )

    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'))
    upgrade_name = Column(String(50), ForeignKey('upgrade_definitions.upgrade_name'), nullable=False)
    level = Column(Integer, default=0)

    user = relationship("User", back_populates="upgrades")
    definition = relationship("UpgradeDefinitions", back_populates="upgrades")

class UpgradeDefinitions(Base):
    __tablename__ = 'upgrade_definitions'
    __table_args__ = (
        PrimaryKeyConstraint('upgrade_name', 'level'),
    )

    upgrade_name = Column(String(50), primary_key=True)
    level = Column(Integer, primary_key=True)
    cost = Column(Integer, nullable=False)
    effect_description = Column(Text)
    upgrades = relationship("Upgrades", back_populates="definition")

class BattleLoadout(Base):
    __tablename__ = 'battle_loadout'

    user_id = Column(
        BigInteger,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True
    )

    weapon = Column(String(50))
    spell = Column(String(50))
    win_streak = Column(Integer, default=0)