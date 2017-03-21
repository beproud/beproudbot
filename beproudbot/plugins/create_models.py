import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime, ForeignKey
from sqlalchemy.orm import relation
from db import Base


class CreatedCommand(Base):
    """語録を登録するコマンドを管理するModel
    """
    __tablename__ = 'created_command'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False, unique=True)
    creator = Column(Unicode(100), nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
    terms = relation('Term', backref='created_commands')


class Term(Base):
    """追加したコマンドに登録する語録を管理するModel
    """
    __tablename__ = 'term'

    id = Column(Integer, primary_key=True)
    created_command = Column(Integer, ForeignKey(
        'created_command.id',
        onupdate='CASCADE',
        ondelete='CASCADE'))
    word = Column(Unicode, nullable=False, unique=True)
    creator = Column(Unicode(100), nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
