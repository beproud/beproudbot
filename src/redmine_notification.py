"""
スクリプト概要
================

systemdでtimerを作成し、定期的に実行

1. Redmineから期限切れ、期限切れそうなチケットを取得
2. チケットの期限によって分類
3. 各チャンネルに期限切れ、期限が切れそうなチケットの情報を通知
"""

import argparse
import time
import logging
import traceback
from configparser import ConfigParser, NoSectionError
from collections import defaultdict
from datetime import timedelta, date, datetime, timezone
from textwrap import dedent

from redminelib import Redmine
from slack import WebClient
from slack.errors import SlackApiError

from db import (
    init_dbsession,
    Session,
    ProjectChannel,
)
from slackbot_settings import (
    REDMINE_URL,
    REDMINE_API_KEY,
    API_TOKEN,
    SQLALCHEMY_URL,
    SQLALCHEMY_ECHO,
    SQLALCHEMY_POOL_SIZE,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# file headerを作る
handler = logging.FileHandler("../logs/redmine_notification.log")
handler.setLevel(logging.INFO)

# logging formatを作る
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

# handlerをloggerに加える
logger.addHandler(handler)

LIMIT = 7  # 期限が1週間以内のチケットを分別するために使用
BOTNAME = "Redmine BOT"  # 通知を送るBOTの名前
EMOJI = ":redmine:"  # BOTの絵文字


def get_ticket_information():
    """Redmineのチケット情報とチケットと結びついているSlackチャンネルを取得"""
    redmine = Redmine(REDMINE_URL, key=REDMINE_API_KEY)
    # すべてのチケットを取得
    issues = redmine.issue.filter(status_id="open", sort="due_date")

    projects_past_due_date = defaultdict(list)
    projects_close_to_due_date = defaultdict(list)
    projects_assigned_to_is_none = defaultdict(list)
    today = date.today()
    close_to_today = today + timedelta(LIMIT)
    s = Session()
    all_proj_channels = s.query(ProjectChannel).all()
    for issue in issues:
        # due_date属性とdue_dateがnoneの場合は除外
        if not getattr(issue, "due_date", None):
            continue
        proj_id = issue.project.id
        # 全てのプロジェクトチャンネルを獲得
        channels = get_proj_channels(proj_id, all_proj_channels)
        if not channels:  # slack channelが設定されていないissueは無視する
            continue
        elif not getattr(issue, "assigned_to", None):
            # 担当者が設定されていないチケットを各プロジェクトごとに抽出
            projects_assigned_to_is_none[issue.project.id].append(issue)
        elif issue.due_date < today:
            # 辞書のkeyと値の例proj_id: ['- 2017-03-31 23872: サーバーセキュリティーの基準を作ろう(@takanory)',]
            projects_past_due_date[proj_id].append(issue)
        # issueの期限が1週間以内の場合
        elif issue.due_date < close_to_today:
            projects_close_to_due_date[proj_id].append(issue)

    # 各プロジェクトのチケット通知をSlackチャンネルに送る。
    send_ticket_info_to_channels(projects_past_due_date, all_proj_channels, True)
    send_ticket_info_to_channels(projects_close_to_due_date, all_proj_channels, False)
    send_assigned_to_is_not_set_tickets(projects_assigned_to_is_none, all_proj_channels)


def display_issue(issues, has_assigned_to=True):
    """issueをSlackのattachmentに格納

    :See: https://api.slack.com/docs/message-attachments

    :param list issues: [redminelib.resources.Issue]
    :param boolean has_assigned_to: issue.assigned_toを表示から除く場合、False
    """
    text = []
    for issue in issues:
        if has_assigned_to:
            text.append(
                "- {}: <{}|#{}> {} (<@{}>)".format(
                    issue.due_date,
                    issue.url,
                    issue.id,
                    issue.subject,
                    issue.assigned_to,
                )
            )
        else:
            text.append(
                "- {}: <{}|#{}> {}".format(
                    issue.due_date, issue.url, issue.id, issue.subject
                )
            )

    attachment = [{"color": "#F44336", "text": "\n".join(text)}]
    return attachment


def send_ticket_info_to_channels(projects, all_proj_channels, is_past_due_date):
    """チャンネルを取得し、チケット情報を各Slackチャンネルごとに通知する。

    :param projects: 期限が切れたプロジェクト、期限が切れそうなプロジェクトのdict
    :param is_past_due_date: 期限切れチケットはTrue,期限が近いチケットはFalse
    """
    for project in projects.keys():
        # api_call()を使用し、すべてのSlackチャンネルに期限が切れたチケット、期限が切れそうな通知をチケットまとめて送る
        # 1つのredmineプロジェクトが複数のslackチャンネルに関連付けられているケースに対応
        channels = get_proj_channels(project, all_proj_channels)
        if channels:
            # プロジェクトごとのチケット数カウントを取得
            issue_count = len(projects[project])
            if is_past_due_date:  # 期限切れチケット
                message = "期限が切れたチケットは{}件です\n".format(issue_count)
            else:  # 期限切れそうなチケット
                message = "もうすぐ期限が切れそうなチケットは{}件です\n".format(issue_count)
            # 通知メッセージをformat
            attachments = display_issue(projects[project])
        for channel in channels:
            send_slack_message_per_sec(channel, attachments, message)


def send_assigned_to_is_not_set_tickets(projects, all_proj_channels):
    """ 担当者が設定されていないチケット一覧を通知する """
    for project in projects.keys():
        channels = get_proj_channels(project, all_proj_channels)
        if channels:
            message = "担当者が設定されていないチケット一覧"
            attachments = display_issue(projects[project], has_assigned_to=False)
        for channel in channels:
            send_slack_message_per_sec(channel, attachments, message)


def get_proj_channels(project_id, all_proj_channels):
    """全てのプロジェクトチャンネルを獲得

    :param project_id: Redmine project id
    :param all_proj_channels: 全てのSlack channel
    """
    for proj_room in all_proj_channels:
        if project_id == proj_room.project_id:
            return proj_room.channels.split(",") if proj_room.channels else []


def send_slack_message(channel, attachments, message):
    """各チャンネルに通知を送る

    :param channel: Slack channel
    :param message: 通知メッセージ
    """
    sc = WebClient(API_TOKEN)
    return sc.api_call(
        "chat.postMessage",
        json={
            "channel": channel,
            "text": message,
            "as_user": "false",
            "icon_emoji": EMOJI,
            "username": BOTNAME,
            "attachments": attachments,
        },
    )


def send_slack_message_per_sec(channel, attachments, message):
    """API rate limitに対処する

    :param channel: Slack channel
    :param message:
    """
    try:
        response = send_slack_message(channel, attachments, message)
    except SlackApiError as e:
        # アーカイブされているチャンネルはスキップ
        if e.response.data["error"] == "is_archived":
            return
        # 通知が失敗なら, responseのrate limit headersをチェック
        elif e.response.data["ok"] is False and e.response.headers.get("Retry-After"):
            # Retry-After headerがどのくらいのdelayが必要かの数値を持っている
            delay = int(e.response.headers["Retry-After"])
            logger.info("Rate limited. Retrying in {} seconds".format(delay))
            time.sleep(delay)
            send_slack_message(channel, attachments, message)

    # メッセージが通知されたかをチェックする
    # メッセージ通知が成功なら、response["ok"]がTrue
    if response["ok"]:
        JST = timezone(timedelta(hours=+9), "JST")
        time_stamp = datetime.fromtimestamp(float(response["message"]["ts"]), JST)
        logger.info("Message posted successfully: {}".format(time_stamp))


def get_argparser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent(
            """\
            説明:
            haroの設定ファイルを読み込んだ後にredmine_notification.pyを実行"""
        ),
    )

    parser.add_argument(
        "-c",
        "--config",
        type=argparse.FileType("r"),
        default="alembic/conf.ini",
        help="ini形式のファイルをファイルパスで指定します",
    )

    return parser


def notify_error(text):
    message = "期限切れチケット通知処理でエラーが発生しました"
    attachment = [{"color": "#F44336", "text": text}]
    # bp-bot-dev チャンネルに通知
    send_slack_message("C0106MV2C4F", attachment, message)


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
    conf["alembic"]["sqlalchemy.url"] = SQLALCHEMY_URL
    conf["alembic"]["sqlalchemy.echo"] = SQLALCHEMY_ECHO
    if SQLALCHEMY_POOL_SIZE:
        conf["alembic"]["sqlalchemy.pool_size"] = SQLALCHEMY_POOL_SIZE
    if not conf.has_section("alembic"):
        raise NoSectionError("alembic")

    init_dbsession(conf["alembic"])
    get_ticket_information()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        notify_error(traceback.format_exc())
