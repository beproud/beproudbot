import json

from redminelib import Redmine
from redminelib.exceptions import ForbiddenError, ResourceNotFoundError

from slackbot.bot import listen_to, respond_to
from slackbot_settings import REDMINE_URL

from db import Session
from haro.plugins.redmine_models import RedmineUser, ProjectChannel

TICKET_INFO = '{}\n{}'
RESPONSE_ERROR = 'Redmineにアクセスできませんでした。'
NO_CHANNEL_PERMISSIONS = '{}は{}で表示できません。'

API_KEY_SET = 'APIキーを保存しました。'
API_KEY_RESET = 'APIキーを削除しました。'
INVALID_API_KEY = 'APIキーは無効です。'
CHANNEL_REGISTERED = 'Redmineの{}プロジェクトをチャンネルに追加しました。'
CHANNEL_UNREGISTERED = 'Redmineの{}プロジェクトをチャンネルから削除しました。'
CHANNEL_ALREADY_REGISTERED = 'このSlackチャンネルは既に登録されています。'
CHANNEL_NOT_REGISTERED = 'このSlackチャンネルは{}プロジェクトに登録されていません。'
PROJECT_NOT_FOUND = 'プロジェクトは見つかりませんでした。'

HELP = """
- `/msg @haro $redmine key <your_api_key>`: 自分のRedmineのAPIキーを登録する
- `$redmine add <redmine_project_identifier>`: コマンドを実行したSlackチャンネルとRedmineのプロジェクトを連携させます
- `$redmine remove <redmine_project_identifier>`: コマンドを実行したSlackチャンネルとRedmineプロジェクトの連携を解除します

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


def project_channel_from_identifier(api_key, identifier, session):
    redmine = Redmine(REDMINE_URL, key=api_key)

    try:
        project = redmine.project.get(identifier.strip())
    except (ForbiddenError, ResourceNotFoundError):
        return None, None

    chan = session.query(ProjectChannel).filter(ProjectChannel.project_id == project.id).\
        one_or_none()
    return project, chan


def user_from_message(message, session):
    # message.bodyにuserが含まれている場合のみ反応する
    if not message.body.get('user'):
        return
    user_id = message.body['user']

    user = session.query(RedmineUser).filter(RedmineUser.user_id == user_id).one_or_none()
    return user


@respond_to('^redmine\s+help$')
def show_help_redmine_commands(message):
    """Redmineコマンドのhelpを表示
    """
    message.send(HELP)


@listen_to('issues\/(\d{2,})|[^a-zA-Z/`\n`][t](\d{2,})|^t(\d{2,})')
def show_ticket_information(message, *ticket_ids):
    """Redmineのチケット情報を参照する.

    :param message: slackbotの各種パラメータを保持したclass
    :param ticket_id: redmineのチケット番号
    """
    s = Session()

    channel = message.channel
    channel_id = channel._body['id']
    user = user_from_message(message, s)
    if not user:
        return
    channels = s.query(ProjectChannel.id).filter(ProjectChannel.channels.contains(channel_id))
    if not s.query(channels.exists()).scalar():
        return

    redmine = Redmine(REDMINE_URL, key=user.api_key)
    for ticket_id in ticket_ids:
        if not ticket_id:
            continue
        try:
            ticket = redmine.issue.get(ticket_id)
        except (ResourceNotFoundError, ForbiddenError):
            message.send(RESPONSE_ERROR)
            return

        proj_id = ticket.project.id
        proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id)\
            .one_or_none()

        if proj_room and channel_id in proj_room.channels.split(','):
            sc = message._client.webapi
            attachments = [{
                "fallback": ticket.description,
                "author_name": str(ticket.author),
                "title": ticket.subject,
                "title_link": ticket.url,
                "text": ticket.description,
                "fields": []
                ,
            }]

            fields = (("担当者", 'assigned_to'),
                      ("ステータス", "status"),
                      ("優先", "priority"), )

            for title, attr in fields:
                value = getattr(ticket, attr, False)
                if value:
                    attachments[0]["fields"].append({
                        "title": title,
                        "value": str(value),
                        "short": True,
                    })

            sc.chat.post_message(channel_id, "", as_user=True, attachments=json.dumps(attachments))
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
    else:
        user.api_key = api_key
    s.commit()
    message.send(API_KEY_SET)


@respond_to('^redmine\s+add\s+(\S+)$')
def register_room(message, project_identifier):
    """RedmineのプロジェクトとSlackチャンネルを繋ぐ.

    :param message: slackbotの各種パラメータを保持したclass
    :param project_identifier: redmineのプロジェクトの識別名
    """
    s = Session()
    channel = message.channel
    channel_id = channel._body['id']

    user = user_from_message(message, s)
    if not user:
        return
    project, project_channel = project_channel_from_identifier(user.api_key, project_identifier, s)
    if not project:
        message.send(PROJECT_NOT_FOUND)
        return

    if not project_channel:
        project_channel = ProjectChannel(project_id=project.id)
        s.add(project_channel)

    channels = project_channel.channels.split(",") if project_channel.channels else []

    if channel_id not in channels:
        channels.append(channel_id)
        project_channel.channels = ",".join(channels)
        s.commit()
        message.send(CHANNEL_REGISTERED.format(project.name))
    else:
        message.send(CHANNEL_ALREADY_REGISTERED)


@respond_to('^redmine\s+remove\s+(\S+)$')
def unregister_room(message, project_identifier):
    s = Session()

    channel = message.channel
    channel_id = channel._body['id']

    user = user_from_message(message, s)
    if not user:
        return

    project, project_channel = project_channel_from_identifier(user.api_key, project_identifier, s)
    if not project:
        message.send(PROJECT_NOT_FOUND)
        return

    if not project_channel:
        return

    try:
        channels = project_channel.channels.split(",") if project_channel.channels else []
        channels.remove(channel_id)
        project_channel.channels = ",".join(channels)
        s.commit()
        message.send(CHANNEL_UNREGISTERED.format(project.name))
    except ValueError:
        message.send(CHANNEL_NOT_REGISTERED.format(project_identifier))
