import csv
from io import StringIO

import requests
from slackbot.bot import respond_to
from slackbot import settings

from db import Session
from haro.botmessage import botsend
from haro.plugins.emergency_models import Timeline, TimelineEntry
from haro.slack import get_user_display_name


NO_ACTIVE_EMERGENCY = '緊急タスクを監視されていません。'
ACTIVE_EMERGENCY = '同時に複数緊急タスクを監視できません。'
ADDED_TO_TIMELINE = '「{}」に追加しました。'
TIMELINE_START = '「{}」という緊急タスクを監視し始めます。'
TIMELINE_END = '「{}」を終了しました。'

MARKDOWN_TEMPLATE = """# {}

タイムライン

{}
"""

HELP = """
- `$emergency start <タイトル>`: コマンドを実行したSlackチャンネルに緊急タスク監視ボットを開始される
- `$emergency update <進捗>`: 監視中緊急タスクのタイムラインに進捗メッセージを追加する
- `$emergency end`: 緊急タスク監視を終了する
- `$emergency list`: コマンドを実行したSlackチャンネルに監視された緊急タスクを一覧に表示をする
- `$emergency timeline <timeline_id>`: 指定したタイムラインをmarkdownで表示される

- `$emergency help`: emergencyのコマンドの使い方を返す
"""


@respond_to('^emergency\s+help$')
def show_help_redmine_commands(message):
    """emergencyコマンドのhelpを表示
    """
    botsend(message, HELP)


def get_active_emergency(session, channel_id):
    return session.query(Timeline).filter(Timeline.room == channel_id,
                                          Timeline.is_closed == False).one_or_none()


@respond_to('^emergency\s+start\s+(\S+)$')
def start_emergency(message, title):
    s = Session()

    title = title.strip()
    if not title:
        return

    user_id = message.body.get('user')
    if not user_id:
        return

    channel_id = message.channel._body['id']

    active_emergency = get_active_emergency(s, channel_id)
    if active_emergency:
        botsend(message, ACTIVE_EMERGENCY)
        return

    timeline = Timeline(created_by=user_id, room=channel_id, title=title, is_closed=False)
    s.add(timeline)
    s.flush()
    entry_msg = TIMELINE_START.format(title)
    entry = TimelineEntry(created_by=user_id, timeline_id=timeline.id, entry=entry_msg)
    s.add(entry)

    s.commit()
    botsend(message, entry_msg)


@respond_to('^emergency\s+update\s+(\S+)$')
def update_emergency(message, entry_msg):
    s = Session()

    entry_msg = entry_msg.strip()
    if not entry_msg:
        return

    user_id = message.body.get('user')
    if not user_id:
        return

    channel_id = message.channel._body['id']

    active_emergency = get_active_emergency(s, channel_id)
    if not active_emergency:
        botsend(message, NO_ACTIVE_EMERGENCY)
        return

    entry = TimelineEntry(created_by=user_id, timeline_id=active_emergency.id, entry=entry_msg)
    s.add(entry)

    s.commit()
    botsend(message, ADDED_TO_TIMELINE.format(active_emergency.title))


@respond_to('^emergency\s+end$')
def end_emergency(message):
    s = Session()

    user_id = message.body.get('user')
    if not user_id:
        return

    channel_id = message.channel._body['id']
    active_emergency = get_active_emergency(s, channel_id)
    if not active_emergency:
        return

    entry_msg = TIMELINE_END.format(active_emergency.title)
    entry = TimelineEntry(created_by=user_id, timeline_id=active_emergency.id, entry=entry_msg)
    s.add(entry)

    active_emergency.is_closed = True
    s.commit()

    botsend(message, entry_msg)


@respond_to('^emergency\s+list$')
def list_emergencies(message):
    s = Session()

    channel_id = message.channel._body['id']
    channel_name = message.channel._body['name']

    timelines = (s.query(Timeline)
                 .filter(Timeline.room == channel_id)
                 .order_by(Timeline.id.desc()))
    rows = [["id", "登録日時", "タイトル"]]
    for t in timelines:
        rows.append([t.id, t.ctime.strftime("%Y/%m/%d"), t.title])

    output = StringIO()
    w = csv.writer(output)
    w.writerows(rows)

    param = {
        'token': settings.API_TOKEN,
        'channels': channel_id,
        'title': '{}の緊急タスク一覧'.format(channel_name)
    }
    requests.post(settings.FILE_UPLOAD_URL,
                  params=param,
                  files={'file': ("%s_emergencies.csv" % channel_name, output.getvalue(),
                                  'text/csv', )})


@respond_to('^emergency\s+timeline\s+(\S+)$')
def show_timeline(message, timeline_id):
    s = Session()

    channel_id = message.channel._body['id']
    channel_name = message.channel._body['name']
    timeline = (s.query(Timeline)
                .filter(Timeline.room == channel_id)
                .filter(Timeline.id == timeline_id)).one_or_none()

    if not timeline:
        return

    entries = (s.query(TimelineEntry)
                 .filter(TimelineEntry.timeline_id == timeline.id)
                 .order_by(TimelineEntry.ctime))

    rows = ['- {} {} {}'.format(
                entry.ctime.strftime("%Y/%m/%d %H:%M"),
                entry.entry,
                get_user_display_name(entry.created_by))
            for entry in entries]

    contents = MARKDOWN_TEMPLATE.format(timeline.title, '\n'.join(rows))

    param = {
        'token': settings.API_TOKEN,
        'channels': channel_id,
        'title': '{}のタイムライン'.format(timeline.title)
    }
    requests.post(settings.FILE_UPLOAD_URL,
                  params=param,
                  files={'file': ("%s_timeline.md" % channel_name, contents,
                                  'text/markdown', )})
