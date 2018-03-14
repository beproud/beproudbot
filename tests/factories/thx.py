import factory
from factory.alchemy import SQLAlchemyModelFactory

from db import ThxHistory
from tests.db import session


class ThxHistoryFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ThxHistory
        sqlalchemy_session = session
        sqlalchemy_session_persistence = 'flush'

    id = factory.Sequence(lambda x: x)
    user_id = factory.Faker('pystr')
    from_user_id = factory.Faker('pystr')
    word = factory.Faker('pystr')
    channel_id = factory.Faker('pystr')
    ctime = factory.Faker('date_time')
