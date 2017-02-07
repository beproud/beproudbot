from utils.slack import get_slack_id_by_name
from beproudbot.plugins.alias_models import UserAliasName


def get_slack_id(session, user_name):
    """指定したユーザー名のSlackのuser_idを返す

    Slackのユーザー名として存在すればAPIからuser_idを取得
    取得できない場合、user_alias_nameにエイリアス名として登録されたユーザー名であれば、
    それに紐づくSlackのuser_idを返す

    :params session: sqlalchemy.orm.Session
    :params str name: ユーザーのエイリアス名
    """
    slack_id = get_slack_id_by_name(user_name)
    if not slack_id:
        slack_id = (session.query(UserAliasName.slack_id)
                    .filter(UserAliasName.alias_name == user_name)
                    .scalar())
    return slack_id
