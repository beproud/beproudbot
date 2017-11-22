import datetime

from sqlalchemy import Column, Integer, Unicode, DateTime

from db import Base


class Uranai(Base):
    """占いの管理に使用されるコマンドのModel
    """
    __tablename__ = 'uranai'

    id = Column(Integer, primary_key=True)
    slack_id = Column(Unicode(11), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
