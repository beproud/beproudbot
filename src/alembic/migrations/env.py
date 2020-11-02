"""
alembic init で生成される設定から以下を変更

- haro のrootパスを追加
- 環境変数からDB設定をロードできるようにする
- db.Base モデルの定義を取得する
"""
from __future__ import with_statement

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Baseをimportするのでharoのrootパスを追加
# NOTE: run.py と統合できない?
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(root)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# ini ファイルに環境変数を渡すことができないため、ここで追加
from slackbot_settings import SQLALCHEMY_URL, SQLALCHEMY_ECHO

config.set_main_option("sqlalchemy.url", SQLALCHEMY_URL)
config.set_main_option("sqlalchemy.echo", SQLALCHEMY_ECHO)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# print("filena", config.config_file_name)
fileConfig(config.config_file_name)


# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# metadata の設定
from db import Base

target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_section["sqlalchemy.url"]
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
