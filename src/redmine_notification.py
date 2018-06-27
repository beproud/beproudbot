from redminelib import Redmine
from db import Session

from haro.plugins.redmine_models import ProjectChannel

from slackbot_settings import REDMINE_URL
from slackbot_settings import API_KEY

def get_ticket_information():
    redmine = Redmine(REDMINE_URL, key=API_KEY)
    # すべてのチケットを取得
    issues = redmine.issue.all(sort='subject:desc')
    s = Session()
    for issue in issues:
        # due_date属性とdue_dateがnoneの場合は除外
        if not getattr(issue, 'due_date', None):
            continue
        print ('%d:%s:%s:%s' % (issue.id, issue.subject, issue.author, issue.due_date))
        # プロジェクトのroomを取得
        proj_id = issue.project.id
        proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id).one_or_none()
        print(proj_room)

def main():
    get_ticket_information()

if __name__ == '__main__':
    main()
