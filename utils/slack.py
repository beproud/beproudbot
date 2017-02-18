import logging

from cachetools.func import ttl_cache
import slacker
from slackbot import settings

logger = logging.getLogger(__name__)


@ttl_cache(ttl=60 * 60 * 10)
def get_users_info():
    """SlackAPIのusersAPIをキャッシュする

    Slacker で users.list API を呼び出す
    - https://github.com/os/slacker
    - https://api.slack.com/methods/users.info

    :return dict: keyがslack_id、valueがユーザー名の辞書
    """
    users = {}
    webapi = slacker.Slacker(settings.API_TOKEN)
    try:
        for d in webapi.users.list().body['members']:
            users[d['id']] = d['name']
    except slacker.Error:
        logger.error('Cannot connect to Slack')
    return users


def get_user_name(user_id):
    """指定された Slack の user_id に対応する username を返す

    :prams str user_id: SlackのユーザーID
    :return str: Slackのユーザー名
    """
    users = get_users_info()
    return users.get(user_id)


def get_slack_id_by_name(name):
    """指定された Slack の user_id に対応する username を返す

    :prams str name: Slackのユーザー名
    :return str or None: Slackのuser_id or None
    """
    users = get_users_info()
    for slack_id, user_name in users.items():
        if user_name == name:
            return slack_id
