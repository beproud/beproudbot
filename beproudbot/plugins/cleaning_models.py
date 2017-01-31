import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime
from db import Base


class Cleaning(Base):
    """掃除当番、各掃除の曜日割当の管理に使用されるコマンドのModel

    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を
        継承したclass
    """
    __tablename__ = 'cleaning'

    id = Column(Integer, primary_key=True)
    slack_id = Column(Unicode(11), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
