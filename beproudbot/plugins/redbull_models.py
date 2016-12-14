import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime
from db import Base


class RedbullHistory(Base):
    """RedBullの本数管理に使用されるコマンドのModel

    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を
        継承したclass
    """
    __tablename__ = 'redbull_history'

    id = Column(Integer, primary_key=True)
    who = Column(Unicode(100))
    delta = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
