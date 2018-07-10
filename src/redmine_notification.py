"""
スクリプト概要
~~~~~~~~~~
systemdでtimerを作成し、定期的に実行するPython
1,Redmineから期限切れ、期限切れそうなチケットを取得する
2,チケットの期限によって分類
3,各チャンネルに期限切れ、期限が切れそうなチケットの情報を通知する。
"""

from redminelib import Redmine
from datetime import timedelta, date
from slackclient import SlackClient
import argparse
from textwrap import dedent
from configparser import ConfigParser, NoSectionError
from collections import defaultdict
import time

from haro.plugins.redmine_models import ProjectChannel

from db import init_dbsession

from slackbot_settings import (
    REDMINE_URL,
    API_KEY,
    SLACK_API_TOKEN,
    SQLALCHEMY_URL,
    SQLALCHEMY_ECHO,
    SQLALCHEMY_POOL_SIZE,
)

from db import Session

LIMIT = 7  # 期限が1週間以内のチケットを分別するために使用


def get_ticket_information():
    """Redmineのチケット情報とチケットと結びついているSlackチャンネルを取得
    """
    redmine = Redmine(REDMINE_URL, key=API_KEY)
    # すべてのチケットを取得
    issues = redmine.issue.filter(status_id='open', sort='due_date')

    projects_past_due_date = defaultdict(list)
    projects_close_to_due_date = defaultdict(list)
    today = date.today()
    close_to_today = today + timedelta(LIMIT)
    for issue in issues:
        # due_date属性とdue_dateがnoneの場合は除外
        if not getattr(issue, 'due_date', None):
            continue
        proj_id = issue.project.id
        # issueのデータをSlack通知用にformatする。
        proj_rooms = get_proj_room(proj_id)

        for proj_room in proj_rooms:
            channels = proj_room.channels
            if not channels:  # slack channelが設定されていないissueは無視する
                continue
            elif issue.due_date < today:
                # 辞書のkeyと値の例proj_id: ['- 2017-03-31 23872: サーバーセキュリティーの基準を作ろう(@takanory)',]
                projects_past_due_date[proj_id].append(issue)
            # issueの期限が1週間以内の場合
            elif issue.due_date < close_to_today:
                projects_close_to_due_date[proj_id].append(issue)

    # 各プロジェクトのチケット通知をSlackチャンネルに送る。
    send_ticket_info_to_channels(projects_past_due_date, True)
    send_ticket_info_to_channels(projects_close_to_due_date, False)


def display_issue(issue):
    """issueの詳細をSlackに表示用にフォーマットする。

    フォーマット例:
    - 2017-03-31 23872: サーバーセキュリティーの基準を作ろう(@takanory)
    :param issue: redmineのissue
    """

    return '- {} {}: {} (@{})'.format(issue.due_date, issue.id,
                                      issue.subject, issue.author)


def send_ticket_info_to_channels(projects, is_past_due_date):
    """チケット情報を各Slackチャンネルごとに通知する。

        :param projects: 期限が切れたプロジェクト、期限が切れそうなプロジェクトのdict
        :param type: int type=0 -> 期限切れ type=1 ->期限切れそうなチケット
    """
    for project in projects.keys():
        # 各プロジェクトのproj_roomを獲得する。
        # TODO: 毎回DBを検索してredmineに紐付いたSlackのチャンネルを取得せず、最初にまとめて取得する
        proj_rooms = get_proj_room(project)

        # api_call()を使用し、すべてのSlackチャンネルに期限が切れたチケット、期限が切れそうな通知をチケットまとめて送る
        # 1つのredmineプロジェクトが複数のslackチャンネルに関連付けられているケースに対応
        for proj_room in proj_rooms:
            channels = proj_room.channels
            # プロジェクトごとのチケット数カウントを取得
            issue_count = len(projects[project])
            if is_past_due_date:  # 期限切れチケット
                message = '期限が切れたチケットは' + str(issue_count) + ' 件です\n'
            else:  # 期限切れそうなチケット
                message = 'もうすぐ期限が切れそうなチケットは' + str(issue_count) + ' 件です\n'
            for issue in projects[project]:
                # 通知メッセージをformatする。
                message += display_issue(issue) + '\n'

            for channel in channels:
                # TODO: JSONでattachmentsを送信する
                send_slack_message_per_sec(channel, message)


def get_proj_room(project_id):
    s = Session()
    return s.query(ProjectChannel).filter(
        ProjectChannel.project_id == project_id).all()


def send_slack_message(channel, message):
    sc = SlackClient(SLACK_API_TOKEN)
    return sc.api_call(
        "chat.postMessage",
        channel=channel,
        text=message
    )


def send_slack_message_per_sec(channel, message):
    """API rate limitに対処する

        :param channel: Slack channel
        :param message:
    """
    response = send_slack_message(channel, message)

    # メッセージが通知されたかをチェックする
    # メッセージ通知が成功なら、response["ok"]がTrue
    if response["ok"]:
        print("Message posted successfully: " + response["message"]["ts"])
        # 通知が失敗なら, responseのrate limit headersをチェック
    elif response["ok"] is False and response["headers"]["Retry-After"]:
        # Retry-After headerがどのくらいのdelayが必要かの数値を持っている
        delay = int(response["headers"]["Retry-After"])
        print("Rate limited. Retrying in " + str(delay) + " seconds")
        time.sleep(delay)
        send_slack_message(message, channel)


def get_argparser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent('''\
            説明:
            haroの設定ファイルを読み込んだ後にslackbotを起動します'''))

    parser.add_argument('-c', '--config',
                        type=argparse.FileType('r'),
                        default='alembic/conf.ini',
                        help='ini形式のファイルをファイルパスで指定します')

    return parser


def main():
    """設定ファイルをparseして、get_ticket_information()を実行する

    1. configparserで設定ファイルを読み込む
    2. 設定ファイルに `alembic` セクションが設定されているかチェック
    3. 設定ファイルの情報でDB周りの設定を初期化
    4. get_ticket_information()を実行する
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
    get_ticket_information()


if __name__ == "__main__":
    main()
