from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Session = sessionmaker()
Base = declarative_base()

# beproudbotでModelを追加した場合、
# alembicでimportしているBaseに紐付けるためModelをimportしてください
# [例]:from beproudbot.plugins.user_models import User # noqa
from beproudbot.plugins.water_models import WaterHistory  # noqa
from beproudbot.plugins.redbull_models import RedbullHistory  # noqa
from beproudbot.plugins.kintai_models import KintaiHistory  # noqa
from beproudbot.plugins.alias_models import UserAliasName  # noqa
from beproudbot.plugins.cleaning_models import Cleaning  # noqa
from beproudbot.plugins.create_models import CreatedCommand, Term  # noqa


def init_dbsession(config, prefix='sqlalchemy.'):
    """configに設定した値でDBの設定情報を初期化

    :param dict config: configから生成したdictの設定値
    :param str prefix: configのoption名から取り除く接頭辞
    :return: `~sqlalchemy.orm.session.Session` インスタンス
    """
    engine = engine_from_config(config, prefix)
    Session.configure(bind=engine)
    Base.metadata.bind = engine
    return Session
