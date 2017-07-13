import requests
from slackbot.bot import respond_to


from db import Session
from beproudbot.plugins.redmine_models import RedmineUser, ProjectRoom

HELP = '''

'''


@respond_to('^#(\d+)')
@respond_to('^t(\d+)')
def show_ticket_information(message, ticket_id):
    """Show redmine ticket information in Slack

    :param message: slackbotの各種パラメータを保持したclass
    :param ticket_id ticket id
    """
    s = Session()

    source_channel = message['channel']
    source_user = message['user']

    user = s.query(RedmineUser).\
        filter(RedmineUser.user_id==source_user).first()

    if user:
        url = "https://project.beproud.jp/redmine/issues/{}".format(ticket_id)
        res = requests.get("{}.json".format(url))
        ticket = res.json()

        proj_room = s.query(ProjectRoom).\
            filter(ProjectRoom.id == ticket["issue"]["project"]["id"]).first()
        if proj_room and source_channel in proj_room:
            message.send("{} {}".format(ticket["issue"]["subject"], url))
    else:
        message.send('{}は登録されていません。'.format(source_user))


