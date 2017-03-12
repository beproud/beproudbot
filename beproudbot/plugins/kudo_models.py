import datetime
from sqlalchemy import Column, Integer, Unicode, DateTime, UniqueConstraint
from db import Base


class KudoHistory(Base):
    """kudoコマンドの管理に使用されるModel
    """
    __tablename__ = 'kudo_history'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    from_user_id = Column(Unicode(100), nullable=False)
    delta = Column(Integer, default=0, nullable=False)
    ctime = Column(DateTime, default=datetime.datetime.now, nullable=False)
    UniqueConstraint('name', 'from_user_id', name='name_from_user_id')
