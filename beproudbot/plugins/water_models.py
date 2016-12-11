import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime
from db import Base


class WaterHistory(Base):
    """Waterの本数管理に使用されるコマンドのModel
    """
    __tablename__ = 'water_history'

    id = Column(Integer, primary_key=True)
    who = Column(Unicode(100))
    delta = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
