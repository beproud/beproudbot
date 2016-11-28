import os
import re
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, declared_attr


class BaseModel():
    """beproudbot base Model
    - beproudbotでModelを定義する際に親クラスで使われるModel
    """
    __table_args__ = {'mysql_engine': 'InnoDB'}

    id = Column(Integer, primary_key=True)

    @declared_attr
    def __tablename__(cls):
        """テーブル名として使われるのでModelClass名をスネークケースに変換"""
        return re.sub('([A-Z])',
                      lambda x: '_' + x.group(1).lower(),
                      cls.__name__).strip('_')

# 強引だがalembicでlocal.iniを選択してDBマイグレーション行い、beproudbot.sqliteファイルがあればlocal環境とする
# TODO: slackbotのrun時にコマンドライン引数のoptionで指定できるようにする
engine = create_engine('sqlite:///beproudbot.sqlite', echo=True)
if not os.path.isfile('beproudbot.sqlite'):
    engine = create_engine('mysql+pymysql://root:password@db/beproudbot?charset=utf8', echo=True)
# beproudbot内の各コマンドコード内でSessionを呼び出してDBに接続を行う
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base(cls=BaseModel)
Base.metadata.bind = engine
