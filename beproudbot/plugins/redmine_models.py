"""redmineのモデル."""
from sqlalchemy import Column, Integer, Unicode
from db import Base


class RedmineUser(Base):
    """SlackのユーザとRedmineのAPI Keyのmap.

    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を
        継承したclass
    """

    __tablename__ = "redmine_users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Unicode(100), nullable=False)  # Slack user id
    api_key = Column(Unicode(100), nullable=False)  # Redmine API Key


class ProjectChannel(Base):
    """Projectはどのチャネルで返してもよいのmap.

    id: Redmine project id
    channels: CSV channel id list i.e. Projectのチケットは定義したチャネルしかに表示しない

    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を継承したclass
    """

    __tablename__ = "redmine_projectchannel"

    id = Column(Integer, primary_key=True)  # Redmineのprojectのid
    channels = Column(Unicode(255), nullable=False)  # "C0AGP8QQH,C0AGP8QQZ"
