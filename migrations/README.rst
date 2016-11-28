alembic
============

1. install alembic
-----------------------

::

   $ pip install alembic


2. initail a alembic [dir]
-----------------------------

::

   $ alembic init alembic


3. check [dir] structure
-----------------------------

::

   [dir]
   |--hoge_models.py      # database model
   |--alembic.ini            # alembic config
   |--alembic/               # alembic file folder
      |--versions/           # versions (delete version = rm file)
      |--env.py              # env setting
      |--README
      |--script.py.mako      # template


4. update alembic.ini change sqlalchemy.url
---------------------------------------------------

::

   sqlalchemy.url = sqlite:///:memory:
   sqlalchemy.url = sqlite:////test.db
   sqlalchemy.url = mysql://username:password@hostname/database

5. new a version
-----------------------

::

   # it will new a python xxxxxx_create_a_new_table.py in versions
   # it include two method upgrade() and downgrade(), need to program it
   $ alembic revision -m 'create a new table'

   def upgrade():
       # 追加するテーブル
        op.create_table(
            'account',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(50), nullable=False),
            sa.Column('description', sa.Unicode(200)),
        )

        # 追加するカラム
        # op.add_column('account', sa.Column('last_transaction_date', sa.DateTime))


    def downgrade():
        # 削除するテーブル
        op.drop_table('account')

        # 削除する列 (not support to sqlite)
        # op.drop_column('account', 'last_transaction_date')

6.upgrade latest database
----------------------------

::

  # database will create a table alembic_version to record current version
  $ alembic upgrade head

7.downgrade to origin database
----------------------------------

::

  $ alembic downgrade base

8.commands
----------------------------------

::

  # upgrade two level
  $ alembic upgrade +2

::

  # downgrade one level
  $ alembic downgrade -1

::

  # upgrade to specific version
  $ alembic upgrade xxxxxxx

::

  # check current version
  $ alembic current
  """ [result]
  $ 3715f217a003 (head)
  """

::

  # check history
  alembic history --verbose
  """ [result]
  Rev: 3715f217a003 (head)
  Parent: <base>
  Path: /Users/data/Desktop/cindy/gomi/npp/alembic/t1/versions/3715f217a003_added_two_columns_to_person_table.py

  added two columns to person table

  Revision ID: 3715f217a003
  Revises:
  Create Date: 2016-11-09 15:54:15.280871
  """

  # -r options
  $ alembic history -r1975ea:ae1027
  $ alembic history -r-3:current
  $ alembic history -r1975ea:
  """ [result]
  <base> -> 3715f217a003 (head), added two columns to person table
  """

9. autogenerate
-------------------------------

1. update env.py

::

   import os
   import sys

   sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "../yourproject/tutorial/Db")))

   from User import User
   from Role import Role
   from Models import Base
   target_metadata = Base.metadata

2. create new version with auto code

::

   $ alembic revision --autogenerate -m "add user table"

10. Use different ini file for alembic.ini
--------------------------------------------------

::

   # use [-c] option
   # alembic -c /path/to/env.ini
   $ alembic -c production.ini upgrade head

