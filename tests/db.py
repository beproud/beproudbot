from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker

from db import Base


class DatabaseManager(object):
    """testでfactoryの設定に使う

    設定の参考は http://momijiame.tumblr.com/post/108317509611/
    TODO: 本当はget_sql_session()なんかもこちらに寄せた方がよさそう。時間と相談
    """

    def __init__(self, test_engine):
        self._engine = test_engine
        self._session_maker = sessionmaker(bind=self._engine)

    def initialize(self):
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)

    @property
    def session(self):
        return self._session_maker()

    @contextmanager
    def transaction(self):
        session = self._session_maker()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
