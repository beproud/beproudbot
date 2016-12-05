from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import ZopeTransactionExtension


Session = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

# beproudbotでModelを追加した場合、
# alembicでimportしているBaseに紐付けるためModelをimportしてください
# [例]:from beproudbot.plugins.user_models import User # noqa


def init_dbsession(config, prefix='sqlalchemy.'):
    """Initialize with setting value so that DB can be used
    :param config: Dictionary generated from config file
    :param prefix: Prefix to match and then strip from keys
        in 'config'.
    :type settings: dict
    :type prefix: str
    :return: `~sqlalchemy.orm.session.Session` instance
    """
    engine = engine_from_config(config, prefix)
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    return Session
