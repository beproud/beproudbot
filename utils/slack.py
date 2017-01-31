import slacker
from slackbot import settings


def get_user_name(user_id):
    """指定された Slack の user_id に対応する username を返す

    Slacker で users.list API を呼び出す
    - https://github.com/os/slacker
    - https://api.slack.com/methods/users.info

    :prams str user_id: SlackのユーザーID
    :return str: Slackのユーザー名
    """
    webapi = slacker.Slacker(settings.API_TOKEN)
    try:
        response = webapi.users.info(user_id)
        return response.body['user']['name']
    except slacker.Error:
        return ''


def get_slack_id_by_name(name):
    """指定された Slack の user_id に対応する username を返す

    :prams str name: Slackのユーザー名
    :return str or None: Slackのuser_id or None
    """
    webapi = slacker.Slacker(settings.API_TOKEN)
    user_id = webapi.users.get_user_id(name)
    return user_id
