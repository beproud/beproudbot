from sqlalchemy import Column, Integer, Unicode, UnicodeText

from db import Base


class Yougo(Base):
    """用語集に使用されるコマンドのModel
    """
    __tablename__ = 'yougo'

    id = Column(Integer, primary_key=True)
    channel_id = Column(Unicode(100), nullable=False)
    project_id = Column(Integer, nullable=False)
    word = Column(Unicode(100), nullable=False)
    english_name = Column(Unicode(100), nullable=True)
    data_type = Column(Unicode(100), nullable=True)
    coding_name = Column(Unicode(100), nullable=True)
    description = Column(UnicodeText, default='')
