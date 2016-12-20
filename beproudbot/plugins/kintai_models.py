import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime, Boolean
from db import Base


class KintaiHistory(Base):
    """勤怠記録に使用されるコマンドのModel
    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を
        継承したclass
    """
    __tablename__ = 'kintai_history'

    id = Column(Integer, primary_key=True)
    who = Column(Unicode(100))
    is_workon = Column(Boolean, default=True)
    ctime = Column(DateTime, default=datetime.datetime.utcnow)
