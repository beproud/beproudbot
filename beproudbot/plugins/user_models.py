import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from db import Base


class User(Base):
    """Slackのuser情報を管理するモデル

    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を
        継承したclass
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_id = Column(Unicode(100), unique=True)
    ctime = Column(DateTime, default=datetime.datetime.utcnow)
    user_name_alias = relationship('UserNameAlias')


class UserNameAlias(Base):
    """Slackのuser_idに紐づく名前を管理するモデル

    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を
        継承したclass
    """
    __tablename__ = 'user_name_alias'

    id = Column(Integer, primary_key=True)
    alias_name = Column(Unicode(100))
    user_id = Column(Integer(unsigned=True),
                     ForeignKey('user.user_id'),
                     onupdate='CASCADE',
                     ondelete='CASCADE')
    ctime = Column(DateTime, default=datetime.datetime.utcnow)
