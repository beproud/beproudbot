"""
    スクリプト概要
    ~~~~~~~~~~

    systemdでtimerを作成し、定期的に実行するPython
    1,Redmineから期限切れ、期限切れそうなチケットを取得する
    2,チケットの期限によって分類
    3,各チャンネルに期限切れ、期限が切れそうなチケットの情報を通知する。

"""

from redminelib import Redmine

from haro.plugins.redmine_models import ProjectChannel

from slackbot_settings import REDMINE_URL, API_KEY
from slackbot.bot import listen_to, respond_to

from haro.botmessage import botsend
from db import Session

@respond_to('^redmine\s+test_daik$')
def get_ticket_information(message):
    """Redmineのチケット情報とチケットと結びついているSlackチャンネルを取得

    """
    redmine = Redmine(REDMINE_URL, key=API_KEY)
    # すべてのチケットを取得
    issues = redmine.issue.all(sort='subject:desc')
    s = Session()
    projects_past_due_date ={}
    projects_close_to_due_date = {}
    for issue in issues:
        # due_date属性とdue_dateがnoneの場合は除外
        if not getattr(issue, 'due_date', None):
            continue
        # プロジェクトのroomを取得
        proj_id = issue.project.id

        # TODO: redmineと関連付けられたSlackチャンネルがない場合の処理
        # TODO: チケットごとに1query走るのは無駄だから、下記以外の方法でprojectのroomを取得する
        # TODO: 1つのredmineプロジェクトが複数のslackチャンネルに関連付けられている場合

        proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id).one_or_none()

        # TODO: 各issueのチェンネルを取得する。方法はredmine.pyのshow_ticket_informationのチャンネル取得方法を参照。

        if check_past_due_date(True): # due_dateがあるIssueを、リストの形で期限切れチケットと期限が切れそうなチケットを分別するFunctionに引き渡す。
            # groupを利用し、同じプロジェクトのidでグループ化する。
            # group issue projects_past_due_date[proj_id]

        elif check_close_to_due_date(True): #  期限が切れそうなチケットをチェックするFunctionを実行
            # groupを利用し、同じプロジェクトのidでグループ化する。
            # group issue projects_close_to_due_date[proj_id]

        else: #期限に余裕があるチケット
            continue

    for project in projects_past_due_date:
        #redmineプロジェクト単位で期限が過ぎたチケットをまとめて通知
        # TODO: 期限切れのチケットカウント数取得
        # (message, '期限が切れたチケットは{}件です'.format('、'.join(projects_past_due_date[project])))
    for project in projects_close_to_due_date:
        # redmineプロジェクト単位で期限が過ぎそうなチケットをまとめて通知
        # TODO: 期限切れのチケットカウント数取得
        # (message, 'もうすぐ期限切れチケットは{}件です'.format('、'.join( each projects_close_to_due_date[project])))
        return True

def check_past_due_date(True):
    """期限切れたチケットをチェックするFunction作成
    期限が切れていたらTrueを返す。それ以外はFalse

    :param tickets: redmineとslackチャンネルのデータを持ったlist

    """

    return True

def check_close_to_due_date(True):
    """期限切れたチケットをチェックするFunction作成
    期限が切れていたらTrueを返す。それ以外はFalse

    :param tickets: redmineとslackチャンネルのデータを持ったlist

    """

    return True
   
 

