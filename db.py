from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Session = sessionmaker()
Base = declarative_base()

# beproudbotでModelを追加した場合、
# alembicでimportしているBaseに紐付けるためModelをimportしてください
# [例]:from beproudbot.plugins.user_models import User # noqa


def init_dbsession(config, prefix='sqlalchemy.'):
    """Initialize with cinfig value so that DB can be used

    :param dict config: Dictionary generated from config file
    :param str prefix: Prefix to match and then strip from keys in 'config'.
    :return: `~sqlalchemy.orm.session.Session` instance
    """
    engine = engine_from_config(config, prefix)
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    return Session
