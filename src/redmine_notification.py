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
    for issue in issues:
        # due_date属性とdue_dateがnoneの場合は除外
        if not getattr(issue, 'due_date', None):
            continue
        print('%d:%s:%s:%s' % (issue.id, issue.subject, issue.author, issue.due_date))
        botsend('%d:%s:%s:%s' % (issue.id, issue.subject, issue.author, issue.due_date))
        # プロジェクトのroomを取得
        proj_id = issue.project.id
        proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id).one_or_none()
        botsend(message, proj_room)


    get_ticket_information()

