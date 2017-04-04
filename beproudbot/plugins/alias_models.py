import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime
from db import Base


class UserAliasName(Base):
    """Slackのuser_idに紐づく名前を管理するモデル
    """
    __tablename__ = 'user_alias_name'

    id = Column(Integer, primary_key=True)
    slack_id = Column(Unicode(100), nullable=False)
    alias_name = Column(Unicode(100), nullable=False, unique=True)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
