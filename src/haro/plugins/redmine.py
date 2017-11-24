from urllib.parse import urljoin

import requests
from slackbot.bot import listen_to, respond_to
from slackbot_settings import REDMINE_URL

from db import Session
from haro.slack import get_user_name
from haro.plugins.redmine_models import RedmineUser, ProjectChannel

USER_NOT_FOUND = '{}はRedmineUserテーブルに登録されていません。'
TICKET_INFO = '{}\n{}'
RESPONSE_ERROR = 'Redmineにアクセスできませんでした。'
NO_CHANNEL_PERMISSIONS = '{}は{}で表示できません。'

API_KEY_SET = 'APIキーを保存しました。'
API_KEY_RESET = 'APIキーを削除しました。'
INVALID_API_KEY = 'APIキーは無効です。'
CHANNEL_REGISTERED = 'Redmineの{}プロジェクトをチャンネルに追加しました。'
CHANNEL_UNREGISTERED = 'Redmineの{}プロジェクトをチャンネルから削除しました。'
PROJECT_NOT_FOUND = 'プロジェクトは見つけませんでした。'

HELP = """
文章の中にチケット番号(tXXXX)が含まれている場合、チケットのタイトル名とチケットのリンクを表示します。

例:
```
james [9:00 PM]
t12345はいつできるのかな？

Haro [9:00 PM]
SlackからRedmineのチケットを見れるようにしよう
http://localhost:9000/redmine/issues/12345
```

- `$redmine help`: redmineのコマンドの使い方を返す
"""


@respond_to('^redmine\s+help$')
def show_help_redmine_commands(message):
    """Redmineコマンドのhelpを表示
    """
    message.send(HELP)


@listen_to('[t](\d{2,})')
def show_ticket_information(message, ticket_id):
    """Redmineのチケット情報を参照する.

    :param message: slackbotの各種パラメータを保持したclass
    :param ticket_id: redmineのチケット番号
    """
    s = Session()

    channel = message.channel
    channel_id = channel._body['id']
    # message.bodyにuserが含まれている場合のみ反応する
    if not message.body.get('user'):
        return
    user_id = message.body['user']

    user = s.query(RedmineUser).filter(RedmineUser.user_id == user_id).one_or_none()

    if not user:
        user_name = get_user_name(user_id)
        message.send(USER_NOT_FOUND.format(user_name))
        return

    channels = s.query(ProjectChannel.id).filter(ProjectChannel.channels.contains(channel_id))
    if not s.query(channels.exists()).scalar():
        return

    ticket_url = urljoin(REDMINE_URL, ticket_id)
    headers = {'X-Redmine-API-Key': user.api_key}
    res = requests.get('{}.json'.format(ticket_url), headers=headers)

    if res.status_code != 200:
        message.send(RESPONSE_ERROR)
        return

    ticket = res.json()
    proj_id = ticket['issue']['project']['id']
    proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id).one_or_none()

    if proj_room and channel_id in proj_room.channels.split(','):
        message.send(TICKET_INFO.format(ticket['issue']['subject'], ticket_url))
    else:
        message.send(NO_CHANNEL_PERMISSIONS.format(ticket_id, channel._body['name']))


@respond_to('^redmine\s+key\s+(\S+)$')
def register_key(message, api_key):
    s = Session()

    if not message.body.get('user'):
        return

    # APIキーは最大40文字となっている。
    api_key = api_key[:40]
    if len(api_key) != 40:
        message.send(INVALID_API_KEY)
        return

    user_id = message.body['user']
    user = s.query(RedmineUser).filter(RedmineUser.user_id == user_id).one_or_none()

    if not user:
        s.add(RedmineUser(user_id=user_id, api_key=api_key))
        s.commit()
        message.send(API_KEY_SET)
        return

    user.api_key = api_key
    s.commit()


@respond_to('^redmine\s+reset$')
def remove_key(message):
    s = Session()

    if not message.body.get('user'):
        return

    user_id = message.body['user']
    user = s.query(RedmineUser).filter(RedmineUser.user_id == user_id).one_or_none()

    if not user:
        return

    user.api_key = ""
    s.commit()


@respond_to('^redmine\s+add\s+(\S+)$')
def register_room(message, project_identifier):
    """Redmineのプロジェクトはチャンネルと繋ぐ.

    :param message: slackbotの各種パラメータを保持したclass
    :param project_identifier: redmineのプロジェクトの識別名
    """
    s = Session()

    channel = message.channel
    channel_id = channel._body['id']

    user = s.query(RedmineUser).filter(RedmineUser.user_id == user_id).one_or_none()

    if not user:
        user_name = get_user_name(user_id)
        message.send(USER_NOT_FOUND.format(user_name))
        return

    channels = s.query(ProjectChannel.id).filter(ProjectChannel.channels.contains(channel_id))
    if not s.query(channels.exists()).scalar():
        return

    # project_url = urljoin(REDMINE_URL, project_identifier)
    # headers = {'X-Redmine-API-Key': user.api_key}
    # res = requests.get('{}.json'.format(ticket_url), headers=headers)
    #
    # if res.status_code != 200:
    #     message.send(RESPONSE_ERROR)
    #     return
    #
    # ticket = res.json()
    # proj_id = ticket['issue']['project']['id']
    # proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id).one_or_none()
    #
    # if proj_room and channel_id in proj_room.channels.split(','):
    #     message.send(TICKET_INFO.format(ticket['issue']['subject'], ticket_url))
    # else:
    #     message.send(NO_CHANNEL_PERMISSIONS.format(ticket_id, channel._body['name']))


@respond_to('^redmine\s+remove$')
def unregister_room(message):
    pass
