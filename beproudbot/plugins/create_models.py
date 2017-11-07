import datetime

from sqlalchemy import Column, Integer, Unicode, DateTime, ForeignKey
from sqlalchemy.orm import relation

from db import Base


class CreateCommand(Base):
    """語録を登録するコマンドを管理するModel
    """
    __tablename__ = 'create_command'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False, unique=True)
    creator = Column(Unicode(100), nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
    terms = relation('Term', backref='create_commands')


class Term(Base):
    """追加したコマンドに登録する語録を管理するModel
    """
    __tablename__ = 'term'

    id = Column(Integer, primary_key=True)
    create_command = Column(Integer, ForeignKey(
        'create_command.id',
        onupdate='CASCADE',
        ondelete='CASCADE'))
    word = Column(Unicode(1024), nullable=False, unique=True)
    creator = Column(Unicode(100), nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
