import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime
from db import Base


class KudoHistory(Base):
    """kudoコマンド(++/--)の管理に使用されるModel
    """
    __tablename__ = 'kudo_history'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    delta = Column(Integer, default=0, nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
