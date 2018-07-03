"""
    スクリプト概要
    ~~~~~~~~~~

    systemdでtimerを作成し、定期的に実行するPython
    1,Redmineから期限切れ、期限切れそうなチケットを取得する
    2,チケットの期限によって分類
    3,各チャンネルに期限切れ、期限が切れそうなチケットの情報を通知する。

"""

from redminelib import Redmine
from datetime import timedelta, datetime
from slackclient import SlackClient

from haro.plugins.redmine_models import ProjectChannel

from slackbot_settings import REDMINE_URL, API_KEY
from slackbot.bot import listen_to, respond_to

from db import Session

@respond_to('^redmine\s+test_daik$')
def get_ticket_information():
    """Redmineのチケット情報とチケットと結びついているSlackチャンネルを取得

    """
    redmine = Redmine(REDMINE_URL, key=API_KEY)
    # すべてのチケットを取得
    issues = redmine.issue.all(sort='subject:desc')

    projects_past_due_date = {}
    projects_close_to_due_date = {}
    for issue in issues:
        # due_date属性とdue_dateがnoneの場合は除外
        if not getattr(issue, 'due_date', None):
            continue
        proj_id = issue.project.id
        # issueのデータをSlack通知用にformatする。
        issue_display = display_issue(issue)
        # issueの期限が過ぎていた場合
       if check_past_due_date(issue.due_date):
           # proj_idをkeyにして値にformatしたIssue情報の値を入れる。
           # 辞書のkeyと値の例:{proj_id: ['- 2017-03-31 23872: サーバーセキュリティーの基準を作ろう(@takanory)'], xxx:['- xxxxxxx']}
            if proj_id not in projects_past_due_date.keys():
                projects_past_due_date[proj_id] = [issue_display]
                print(issue_display)
            else:
                projects_past_due_date[proj_id].append(issue_display)
        # issueの期限が1週間以内の場合
        elif check_close_to_due_date(issue.due_date):
            if proj_id not in projects_close_to_due_date.keys():
                 projects_close_to_due_date[proj_id] = [issue_display]
            else:
                projects_close_to_due_date[proj_id].append(issue_display)
        else:
            continue

    # 各プロジェクトのチケット通知をSlackチャンネルに送る。
    send_ticket_info_to_channels(projects_past_due_date)
    send_ticket_info_to_channels(projects_close_to_due_date)

def display_issue(issue):
    """issueの詳細をSlackに表示用にフォーマットする。

    　 :param issue: redmineのissue
    """

    return '- ' + str(issue.due_date) + ' ' + str(issue.id) + ': ' + str(issue.subject) + '(@' + str(issue.author) + ')'

def check_past_due_date(due_date):
    """期限切れたチケットをチェックするFunction
    期限が切れていたらTrueを返す。それ以外はFalse

    :param due_date: チケットのdue_date

    """
    # TODO: due_dateが過ぎたチケットをチェックするコード作成
    return True

def check_close_to_due_date(due_date):
    """期限が1週間以内に切れそうなチケットをチェックするFunction
    期限が切れていたらTrueを返す。それ以外はFalse

    :param due_date: チケットのdue_date

    """
    # TODO: due_dateが1週間切ったチケットをチェックするコード作成
    return True

def send_ticket_info_to_channels(projects):
    """期限が1週間以内に切れそうなチケットをチェックするFunction
        期限が切れていたらTrueを返す。それ以外はFalse

        :param projects: 期限が切れたプロジェクト、期限が切れそうなプロジェクトのdict

    """
    s = Session()
    sc = SlackClient(SLACK_API_TOKEN)
    for project in projects.keys():
        # 各プロジェクトのproj_roomを獲得する。
        proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == project).one_or_none()
        # TODO: 各プロジェクトの通知チケット数をカウント

        # api_call()を使用し、すべてのSlackチャンネルに期限が切れたチケット、期限が切れそうな通知をチケットまとめて送る
        if proj_room:
            # 1つのredmineプロジェクトが複数のslackチャンネルに関連付けられているケースに対処
            channels = proj_room.channels
            for channel in channels:
                sc.api_call(
                    "chat.postMessage",
                    channel=channel,
                    text='期限が切れたチケットは{}件です'.format(
                        '、'.join(projects[project]))
                )
