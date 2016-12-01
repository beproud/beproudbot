from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Session = sessionmaker()
Base = declarative_base()

# beproudbotでModelを追加した場合、
# alembicでimportしているBaseに紐付けるためModelをimportしてください
# [例]:from beproudbot.plugins.user_models import User # noqa


def init_dbsession(settings, prefix='sqlalchemy.'):
    """beproudbotのModelとDBの紐付けを行う
    """
    engine = engine_from_config(settings, prefix)
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    return Session
