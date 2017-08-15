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
    user_id = Column(Unicode(100), nullable=False)  # Slack username
    api_key = Column(Unicode(100), nullable=False)  # Redmine API Key


class ProjectRoom(Base):
    """Projectはどのチャネルで返してもよいのmap.

    id: Redmine project id
    rooms: CSV room list i.e. this project's tickets can only be replied to in these rooms

    :param Base: `sqlalchemy.ext.declarative.api.DeclarativeMeta` を
        継承したclass
    """

    __tablename__ = "remine_projectroom"

    id = Column(Integer, primary_key=True)  # Redmineのprojectのid
    rooms = Column(Unicode(255), nullable=False)  # "slack-api-practice,bp-kaizen"
