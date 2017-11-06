from sqlalchemy import Column, Integer, Unicode

from db import Base


class RedmineUser(Base):
    """SlackのユーザとRedmineのAPI Keyのmap."""

    __tablename__ = "redmine_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Unicode(9), nullable=False, unique=True, doc="""
    Slackのユーザid
    例: U023BECGF
    """)
    api_key = Column(Unicode(40), nullable=False, unique=True, doc="""
    RedmineのAPIのKey
    https://project.beproud.jp/redmine/my/accountの右側で見つかります。

    例: d1d567978001e4f884524a8941a9bbe6a8be87ac
    """)


class ProjectChannel(Base):
    """Projectはどのチャネルで返してもよいのmap."""

    __tablename__ = "redmine_projectchannel"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, unique=True, doc="""
    Redmineのprojectのid
    """)
    channels = Column(Unicode(249), nullable=False, doc="""
    CSV channel id list.
    i.e. Projectのチケットは定義したチャネルしかに表示しない
    例: "C0AGP8QQH,C0AGP8QQZ"

    25チャネルまで登録できる.
    9 (チャネルの長さ) * 25 = 225 + 24 (,の数) = 249

    """)
