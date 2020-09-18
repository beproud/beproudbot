from redminelib import Redmine
from redminelib.exceptions import ForbiddenError, ResourceNotFoundError
from slackbot.bot import listen_to, respond_to
from slackbot_settings import REDMINE_URL
from db import Session
from haro.botmessage import botsend
from haro.plugins.redmine_models import RedmineUser, ProjectChannel

RESPONSE_ERROR = 'Redmineにアクセスできませんでした。'
NO_CHANNEL_PERMISSIONS = '{}は{}で表示できません。'
NO_TEXT = '(本文なし)'

API_KEY_SET = 'APIキーを保存しました。'
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
- ※<your_api_key> はRedmineの `[個人設定] -> [APIアクセスキー] -> [表示]` から取得します
- ※<redmine_project_identifier> はRedmineのプロジェクトを開き、 `[設定] -> [情報] -> [識別子]` から取得します

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

    chan = session.query(ProjectChannel).filter(ProjectChannel.project_id == project.id). \
        one_or_none()
    return project, chan


def user_from_message(message, session):
    # message.bodyにuserが含まれている場合のみ反応する
    if not message.body.get('user'):
        return
    user_id = message.body['user']

    user = session.query(RedmineUser).filter(RedmineUser.user_id == user_id).one_or_none()
    return user


@respond_to(r'^redmine\s+help$')
def show_help_redmine_commands(message):
    """Redmineコマンドのhelpを表示
    """
    botsend(message, HELP)


@listen_to(r'issues\/(\d{2,}\#note\-\d+)|issues\/(\d{2,})|[^a-zA-Z/`\n`][t](\d{2,})|^t(\d{2,})')  # NOQA: R701,C901,E501
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

        noteno = None
        note_suffix = ""
        if '#note-' in ticket_id:
            ticket_id, noteno = ticket_id.split('#note-')
            note_suffix = "#note-{}".format(noteno)

        try:
            ticket = redmine.issue.get(ticket_id)
        except (ResourceNotFoundError, ForbiddenError):
            botsend(message, RESPONSE_ERROR)
            return

        proj_id = ticket.project.id
        proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id) \
            .one_or_none()

        if not proj_room or channel_id not in proj_room.channels.split(','):
            botsend(message, NO_CHANNEL_PERMISSIONS.format(ticket_id, channel._body['name']))
            return

        if noteno:
            description = None
            # Redmine 側で変更がなければ問題ないけど、
            # values には #note-n に相当するidがはいっていないので
            # id でソートして順番を保証している
            notes = sorted(ticket.journals.values(), key=lambda d: d['id'])
            for i, v in enumerate(notes, start=1):
                if str(i) == noteno:
                    # コメントの本文があれば取得する
                    if v.get('notes'):
                        description = v['notes']
            # コメント本文がなかったら書き換えられるよう仮文言としている
            if not description:
                description = NO_TEXT
        else:
            # デフォルトでは説明欄の本文を使用する
            description = ticket.description or NO_TEXT

        text = "#{ticketno}{noteno}: [{assigned_to}][{priority}][{status}] {title}".format(
            ticketno=ticket_id,
            noteno=note_suffix,
            assigned_to=getattr(ticket, "assigned_to", "担当者なし"),
            priority=getattr(ticket, "priority", "-"),
            status=getattr(ticket, "status", "-"),
            title=ticket.subject,
        )
        url = "{}{}".format(ticket.url, note_suffix)

        sc = message._client.webapi
        res = sc.chat.post_message(channel_id, "<{}|{}>".format(url, text), as_user=True)
        sc.chat.post_message(channel_id, description, as_user=True, thread_ts=res.body['ts'])


@respond_to(r'^redmine\s+key\s+(\S+)$')
def register_key(message, api_key):
    s = Session()

    if not message.body.get('user'):
        return

    # APIキーは最大40文字となっている。
    api_key = api_key[:40]
    if len(api_key) != 40:
        botsend(message, INVALID_API_KEY)
        return

    user_id = message.body['user']
    user = s.query(RedmineUser).filter(RedmineUser.user_id == user_id).one_or_none()

    if not user:
        s.add(RedmineUser(user_id=user_id, api_key=api_key))
    else:
        user.api_key = api_key
    s.commit()
    botsend(message, API_KEY_SET)


@respond_to(r'^redmine\s+add\s+([a-zA-Z0-9_-]+)$')
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
        botsend(message, PROJECT_NOT_FOUND)
        return

    if not project_channel:
        project_channel = ProjectChannel(project_id=project.id)
        s.add(project_channel)

    channels = project_channel.channels.split(",") if project_channel.channels else []

    if channel_id not in channels:
        channels.append(channel_id)
        project_channel.channels = ",".join(channels)
        s.commit()
        botsend(message, CHANNEL_REGISTERED.format(project.name))
    else:
        botsend(message, CHANNEL_ALREADY_REGISTERED)


@respond_to(r'^redmine\s+remove\s+([a-zA-Z0-9_-]+)$')
def unregister_room(message, project_identifier):
    s = Session()

    channel = message.channel
    channel_id = channel._body['id']

    user = user_from_message(message, s)
    if not user:
        return

    project, project_channel = project_channel_from_identifier(user.api_key, project_identifier, s)
    if not project:
        botsend(message, PROJECT_NOT_FOUND)
        return

    if not project_channel:
        return

    try:
        channels = project_channel.channels.split(",") if project_channel.channels else []
        channels.remove(channel_id)
        project_channel.channels = ",".join(channels)
        s.commit()
        botsend(message, CHANNEL_UNREGISTERED.format(project.name))
    except ValueError:
        botsend(message, CHANNEL_NOT_REGISTERED.format(project_identifier))
