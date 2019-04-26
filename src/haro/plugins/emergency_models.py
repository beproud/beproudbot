from datetime import datetime

from sqlalchemy import Column, Integer, Unicode, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from db import Base


class Timeline(Base):
    """緊急タスクのタイムライン"""

    __tablename__ = "emergency_timeline"

    id = Column(Integer, primary_key=True)
    created_by = Column(Unicode(9), nullable=False, doc="""
    Slackのユーザid
    例: U023BECGF
    """)
    room = Column(Unicode(9), nullable=False, doc="""
    Slackのチャネルかグループid
    例: C1H9RESGL
    """)

    title = Column(Unicode(128), nullable=False, doc="""
    緊急タスクのタイトル
    例: 本番のDBに接続できない
    """)

    ctime = Column(DateTime, default=datetime.now, nullable=False, doc="""
    登録した日時
    """)
    utime = Column(DateTime, default=datetime.now, nullable=False, doc="""
    更新した日時
     """)
    entries = relationship("TimelineEntry")


class TimelineEntry(Base):
    """緊急タスクのタイムラインログ"""

    __tablename__ = "timeline_log"

    id = Column(Integer, primary_key=True)
    timeline_id = Column(Integer, ForeignKey('timeline.id'), nullable=False)
    created_by = Column(Unicode(9), nullable=False, doc="""
    Slackのユーザid
    例: U023BECGF
    """)
    ctime = Column(DateTime, default=datetime.now, nullable=False, doc="""
    登録した日時
    """)
    utime = Column(DateTime, default=datetime.now, nullable=False, doc="""
    更新した日時
     """)
    entry = Column(Text, nullable=False, doc="""
    緊急タスクの進捗テキスト
    """)
