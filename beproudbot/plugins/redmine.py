import requests
from slackbot.bot import respond_to


from db import Session
from beproudbot.plugins.redmine_models import RedmineUser, ProjectRoom

HELP = '''

'''


@respond_to('^#(\d+)')
def show_ticket_information(message, ticket_id):
    """現在の水の在庫本数を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    :param ticket_id ticket id
    """
    s = Session()

    source_channel = message['channel']
    source_user = message['user']

    user = s.query(RedmineUser).\
        filter(RedmineUser.user_id==source_user).first()

    if user:
        res = requests.get("https://project.beproud.jp/redmine/issues/{}.json".format(ticket_id))
        ticket = res.json()

        proj_room = s.query(ProjectRoom).filter(ProjectRoom.id==ticket["issue"]["project"]["id"]).\
            first()
        if proj_room and source_channel in proj_room:
            message.send(ticket["issue"]["subject"])
    else:
        message.send('{}は登録されていません。'.format(source_user))


