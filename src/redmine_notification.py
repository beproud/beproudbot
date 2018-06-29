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
        print(proj_id)
        proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id).one_or_none()
        print(proj_room)

        # 各issueのチェンネルを取得する。方法はredmine.pyのshow_ticket_informationのチャンネル取得方法を参照。

        # if True: due_dateがあるIssueを、リストの形で期限切れチケットと期限が切れそうなチケットを分別するFunctionに引き渡す。
            # text = str(issue.id) +'タイトル: '+ str(issue.subject) + ' 責任者: '+ str(issue.author) + 'チケットの期限が過ぎてます。'+ str(issue.due_date)
            # sc.chat.post_message()メソッドを利用して各チャンネルに期限切れチケット情報を送付


            # else :Falseの場合
               # if True: 期限が切れそうなチケットをチェックするファンクションを実行
                        #     text = str(issue.id) +'タイトル: '+ str(issue.subject) + ' 責任者: '+ str(issue.author) + 'チケットの期限が切れそうです。'+ str(issue.due_date)
                        # 　  sc.chat.post_message()メソッドを使って、チケット情報を各チャンネルに送付
        　
                # else: 期限に余裕があるチケット
        　　　　　　　# continue
        　　　　　　
"""期限切れたチケットをチェックするFunction作成
   期限が切れていたらTrueを返す。それ以外はFalse
   
 
　　:param tickets: redmineとslackチャンネルのデータを持ったlist
    
"""

"""期限切そうなチケットをチェックするFunction
   期限が切れそうだったらTrueを返す。それ以外はFalse


　　:param tickets: redmineとslackチャンネルのデータを持ったlist
"""
