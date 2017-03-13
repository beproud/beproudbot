import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime, ForeignKey
from sqlalchemy.orm import relation
from db import Base


class CreatedCommand(Base):
    """用語(語録)を登録するコマンドを管理するModel
    """
    __tablename__ = 'created_command'

    id = Column(Integer, primary_key=True)
    command = Column(Unicode(100), nullable=False)
    creator = Column(Unicode(100), nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
    registered_term = relation('RegisteredTerm', backref='created_command', uselist=False)


class RegisteredTerm(Base):
    """追加したコマンドに登録する用語(語録)を管理するModel
    """
    __tablename__ = 'registered_term'

    id = Column(Integer, primary_key=True)
    command = Column(Integer, ForeignKey(
        'created_command.id',
        onupdate='CASCADE',
        ondelete='CASCADE'))
    term = Column(Unicode, nullable=False)
    creator = Column(Unicode(100), nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
