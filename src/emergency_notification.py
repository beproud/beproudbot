"""
スクリプト概要
================

systemdでtimerを作成し、定期的に実行

1. DBから、最終更新からKEEP-ALIVE-MINUTESを過ぎた緊急タイムラインを取得
3. 各チャンネルに更新を促すメッセージを通知
"""

import argparse
import time
import logging
from configparser import ConfigParser, NoSectionError
from datetime import timedelta, datetime, timezone
from textwrap import dedent

from slackclient import SlackClient

from db import (
    init_dbsession,
    Session
)
from slackbot_settings import (
    API_TOKEN,
    SQLALCHEMY_URL,
    SQLALCHEMY_ECHO,
    SQLALCHEMY_POOL_SIZE
)
from haro.slack import get_user_name
from haro.plugins.emergency_models import Timeline, TimelineEntry

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# file headerを作る
handler = logging.FileHandler('../logs/emergency_notification.log')
handler.setLevel(logging.INFO)

# logging formatを作る
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# handlerをloggerに加える
logger.addHandler(handler)

# Slackクライアント
slack_client = SlackClient(API_TOKEN)

KEEP_ALIVE_MINUTES = 60  # 何分更新がなかったら通知するか(デフォルト)
BOT_NAME = 'Emergency BOT'  # 通知を送るBOTの名前
MESSAGE_EMOJI = ':rotating_light:'  # メッセージの絵文字
ICON_EMOJI = ':rotating_light:'  # BOTの絵文字


def send_keep_alive_message(keep_alive_minutes):
    """更新時間を過ぎた緊急タイムラインの情報を通知"""
    keep_alive_target_time = datetime.now() - timedelta(minutes=keep_alive_minutes)
    s = Session()
    timelines = (s.query(Timeline)
                 .filter(Timeline.is_closed.is_(False))
                 .filter(Timeline.utime < keep_alive_target_time))
    for timeline in timelines:
        channel = timeline.room
        message = '{}「{}」の状況を更新してください。{}'.format(
            MESSAGE_EMOJI, timeline.title, MESSAGE_EMOJI)
        attachment = get_history_as_attachment(timeline)
        send_message_to_slack_over_limit(channel, message, [attachment])


def get_history_as_attachment(timeline):
    """緊急タイムラインの履歴をSlackのattachmentとして取得"""
    s = Session()
    histories = (s.query(TimelineEntry)
                 .filter(TimelineEntry.timeline_id == timeline.id)
                 .order_by('utime'))
    texts = [
        '- {} {} <@{}>'.format(history.utime.strftime('%Y/%m/%d %H:%M'),
                               history.entry,
                               get_user_name(history.created_by))
        for history in histories
    ]
    attachment = {
        'color': '#ff0000',
        'text': '\n'.join(texts),
    }
    return attachment


def send_message_to_slack(channel, message, attachments):
    """Slackにメッセージを送信します"""
    response = slack_client.api_call(
        'chat.postMessage',
        channel=channel,
        text=message,
        as_user="false",
        icon_emoji=ICON_EMOJI,
        username=BOT_NAME,
        attachments=attachments
    )
    return response


def send_message_to_slack_over_limit(channel, message, attachments):
    """API制限を考慮してSlackにメッセージを送信します"""
    response = send_message_to_slack(channel, message, attachments)

    # メッセージが通知されたかをチェックする
    # メッセージ通知が成功なら、response['ok]がTrue
    if response['ok']:
        jst_tz = timezone(timedelta(hours=+9), 'JST')
        time_stamp = datetime.fromtimestamp(
            float(response['message']['ts']),
            jst_tz
        )
        logger.info("Message posted successfully: {}".format(time_stamp))
    # 通知が失敗なら, API制限を抜けたタイミングで再送
    elif not response['ok']:
        # Retry-After headerがどのくらいのdelayが必要かの数値を持っている
        delay = int(response['headers']['Retry-After'])
        logger.info("Rate limited. Retrying in {} seconds".format(delay))
        time.sleep(delay)
        send_message_to_slack(channel, message, attachments)


def get_argparser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent('''\
            説明:
            haroの設定ファイルを読み込んだ後にemergency_notification.pyを実行'''))

    parser.add_argument('-c', '--config',
                        type=argparse.FileType('r'),
                        default='alembic/conf.ini',
                        help='ini形式のファイルをファイルパスで指定します')
    parser.add_argument('-k', '--keep_alive_minutes',
                        type=int,
                        default=KEEP_ALIVE_MINUTES,
                        help='何分更新されなかったら通知するか')
    return parser


def main():
    """設定ファイルをparseして、send_keep_alive_message()を実行する

    1. configparserで設定ファイルを読み込む
    2. 設定ファイルに `alembic` セクションが設定されているかチェック
    3. 設定ファイルの情報でDB周りの設定を初期化
    4. send_keep_alive_message()を実行する
    """
    parser = get_argparser()
    args = parser.parse_args()
    conf = ConfigParser()
    conf.read_file(args.config)
    # 環境変数で指定したいため ini ファイルでなくここで追記
    conf["alembic"]['sqlalchemy.url'] = SQLALCHEMY_URL
    conf["alembic"]['sqlalchemy.echo'] = SQLALCHEMY_ECHO
    if SQLALCHEMY_POOL_SIZE:
        conf["alembic"]['sqlalchemy.pool_size'] = SQLALCHEMY_POOL_SIZE
    if not conf.has_section('alembic'):
        raise NoSectionError('alembic')

    init_dbsession(conf['alembic'])
    send_keep_alive_message(args.keep_alive_minutes)


if __name__ == '__main__':
    main()
