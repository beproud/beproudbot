import datetime

from sqlalchemy import Column, Integer, Unicode, DateTime
from db import Base


class ThxHistory(Base):
    """thxの管理に使用されるコマンドのModel
    """
    __tablename__ = 'thx_history'

    id = Column(Integer, primary_key=True)
    user_id = Column(Unicode(100), nullable=False)
    from_user_id = Column(Unicode(100), nullable=False)
    word = Column(Unicode(1024), nullable=False)
    channel_id = Column(Unicode(100), nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
