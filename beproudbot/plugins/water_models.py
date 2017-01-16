import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime
from db import Base


class WaterHistory(Base):
    """Waterの本数管理に使用されるコマンドのModel

    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を
        継承したclass
    """
    __tablename__ = 'water_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Unicode(100), unique=True)
    delta = Column(Integer, default=0)
    ctime = Column(DateTime, default=datetime.datetime.utcnow)
