import datetime

from sqlalchemy import Column, Integer, Unicode, DateTime

from db import Base


class Resource(Base):
    """StatusコマンドのリソースのModel
    """
    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Unicode(249), nullable=False)
    name = Column(Unicode(249), nullable=False)
    status = Column(Unicode(249), nullable=True)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
