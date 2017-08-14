import requests
import json
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

        # encoding headerは嘘ついてる、UTF-8ではなく　iso2022-jpです
        # Still need to debug this - coding as iso2022-jp lets me return
        # a url, but it strips all Japanese from the message (not useful).
        # This may be an LC environment variable issue.
        ticket = json.loads(res.content.decode("iso2022-jp", "ignore"))

        # proj_room = s.query(ProjectRoom).\
        #   filter(ProjectRoom.id == ticket["issue"]["project"]["id"]).first()
        #if proj_room and source_channel in proj_room:

        message.send("{} {}".format(ticket["issue"]["subject"], url))
    else:
        message.send('{}は登録されていません。'.format(source_user))


