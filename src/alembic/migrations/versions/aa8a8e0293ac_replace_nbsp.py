"""replace &nbsp

Revision ID: aa8a8e0293ac
Revises: 98ecbc1e5b66
Create Date: 2020-11-02 12:48:17.045798

"""
import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from alembic import op
from haro.plugins.create_models import Term

# revision identifiers, used by Alembic.
revision = 'aa8a8e0293ac'
down_revision = '98ecbc1e5b66'
branch_labels = None
depends_on = None

engine = sa.create_engine(os.environ.get("SQLALCHEMY_URL"))
Session = sessionmaker(bind=engine)

def upgrade():
    # ハイパーリンクがTerm.wordに含まれている場合、半角スペースが\xa0になってしまっているケースが存在するため置き換える
    s = Session()
    terms = s.query(Term).filter(Term.word.like('%\xa0%'))
    print(terms)
    for term in terms:
        term.word = term.word.replace('\xa0', ' ')
    s.commit()


def downgrade():
    pass
