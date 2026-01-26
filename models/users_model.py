from sqlalchemy import Column, ForeignKey, BigInteger, String, Integer, SmallInteger, TIMESTAMP, Boolean, PrimaryKeyConstraint, Text, func, CheckConstraint
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
    campaign_stage = Column(Integer, default=1)
    starter_loan_given = Column(Boolean, nullable=False, default=False)
    notif = Column(Boolean, nullable=False, default=True)

    wallet = relationship('Wallet', back_populates='user', uselist=False, cascade='all, delete')
    inventory = relationship('Inventory', back_populates='user', cascade='all, delete')
    marketplace = relationship('Marketplace', back_populates = 'user')
    upgrades = relationship("Upgrades", back_populates="user")
    quests = relationship("Quests", back_populates="user", uselist=False, cascade="all, delete")
    user_stats = relationship("UserStats", back_populates="user", uselist=False, cascade="all, delete")

    friendship = relationship(
        "Friendship",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    battle_loadout = relationship(
        "BattleLoadout",
        back_populates="user",
        uselist=False,
        cascade="all, delete"
    )

    loans = relationship(
        'Loan',
        back_populates='user',
        cascade='all, delete'
    )

class UserStats(Base):
    __tablename__ = 'user_stats'

    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    battles_won = Column(Integer, default=0)
    races_won = Column(Integer, default=0)
    longest_quest_streak = Column(Integer, default=0)
    weekly_rank1_count = Column(Integer, default=0)
    biggest_lottery_win = Column(Integer, default=0)
    updated_at = Column(TIMESTAMP, default=func.now())

    user = relationship("User", back_populates="user_stats")


class Wallet(Base):
    __tablename__ = 'wallet'

    user_id = Column(BigInteger, ForeignKey('users.user_id', ondelete='CASCADE'), primary_key=True)
    gold = Column(Integer, default=0)
    chip = Column(Integer,default=0)

    user = relationship("User", back_populates="wallet")

class Quests(Base):
    __tablename__ = 'quests'

    user_id = Column(
        BigInteger,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True
    )

    delivery_items = Column(JSONB, default=list)
    reward = Column(Integer, default=0)
    limit = Column(Integer, default=0)
    skips = Column(Integer, default=0)
    streak = Column(Integer, default=0)
    rerolls = Column(Integer, default=0)

    user = relationship("User", back_populates="quests")



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

    user_id = Column(
        BigInteger,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        primary_key=True
    )
    friendship_exp = Column(Integer, default=0)
    daily_exp = Column(Integer, default=0)

    user = relationship("User", back_populates="friendship")

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

    user = relationship("User", back_populates="battle_loadout")


# Loans model
class Loan(Base):
    __tablename__ = 'loans'

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    loan_pack_id = Column(Integer, nullable=False)

    status = Column(String, nullable=False, default='active')

    issued_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    due_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)

    paid_at = Column(TIMESTAMP(timezone=True), nullable=True)
    defaulted_at = Column(TIMESTAMP(timezone=True), nullable=True)

    due_reminder_sent = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        CheckConstraint(
            'NOT (paid_at IS NOT NULL AND defaulted_at IS NOT NULL)',
            name='loans_paid_or_defaulted_check'
        ),
    )

    user = relationship('User', back_populates='loans')


# Invites model
class Invites(Base):
    __tablename__ = 'invites'
    __table_args__ = (
        PrimaryKeyConstraint('inviter_id', 'invited_id'),
    )

    inviter_id = Column(
        BigInteger,
        ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False
    )

    invited_id = Column(
        BigInteger,
        nullable=False,
        unique=True
    )

    rewarded = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    inviter = relationship(
        "User",
        foreign_keys=[inviter_id]
    )