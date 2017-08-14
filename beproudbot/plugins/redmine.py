import requests
from slackbot.bot import listen_to


from db import Session
from beproudbot.plugins.redmine_models import RedmineUser, ProjectRoom

HELP = '''

'''


@listen_to('[t#](\d+)')
def show_ticket_information(message, ticket_id):
    """Show redmine ticket information in Slack

    :param message: slackbotの各種パラメータを保持したclass
    :param ticket_id ticket id
    """
    s = Session()

    channel = message.channel
    source_channel = channel._body['name']
    source_user = channel._client.users[message.body['user']][u'name']

    user = s.query(RedmineUser).\
        filter(RedmineUser.user_id == source_user).first()

    if user:
        url = "https://project.beproud.jp/redmine/issues/{}".format(ticket_id)
        headers = {'X-Redmine-API-Key': user.api_key}
        res = requests.get("{}.json".format(url), headers=headers)
        ticket = res.json()

        # proj_room = s.query(ProjectRoom).\
        #   filter(ProjectRoom.id == ticket["issue"]["project"]["id"]).first()
        #if proj_room and source_channel in proj_room:
        message.send("{} {}".format(ticket["issue"]["subject"], url))
    else:
        message.send('{}は登録されていません。'.format(source_user))


