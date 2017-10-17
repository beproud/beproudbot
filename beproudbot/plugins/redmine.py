import os
from urllib.parse import urljoin

import requests
from slackbot.bot import listen_to, respond_to

from db import Session
from utils.slack import get_user_name

from .redmine_models import RedmineUser, ProjectChannel

REDMINE_URL = os.environ.get('REDMINE_URL', 'https://project.beproud.jp/redmine/issues/')

USER_NOT_FOUND = '{}はRedmineUserテーブルに登録されていません。'
TICKET_INFO = '{}\n{}'
RESPONSE_ERROR = 'Redmineにアクセスできませんでした。'
NO_CHANNEL_PERMISSIONS = '{}は{}で表示できません。'


HELP = """
beproudbotは文章の中の t<チケットid> を探し、見つかる祭、チケットへのリンクを返す。

例:
> t56147はいつできるのかな？
< SlackとRedmineとつながりたいです。
< https://project.beproud.jp/redmine/issues/56147


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
