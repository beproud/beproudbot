from slackbot.bot import respond_to

from db import Session
from haro.botmessage import botsend
from haro.plugins.emergency_models import Timeline, TimelineEntry


ACTIVE_EMERGENCY = '同時に複数緊急タスクを管理できません。'
TIMELINE_START = '「{}」という緊急タスクを監視し始めます。'
TIMELINE_END = '「{}」を終了しました。'

HELP = """
- `$emergency start <タイトル>`: コマンドを実行したSlackチャンネルに緊急タスク監視ボットを開始される


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
