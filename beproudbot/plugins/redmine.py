"""redmineのチケット情報を参照."""
import logging

import requests
from slackbot.bot import listen_to

from db import Session
from utils.slack import get_user_name
from beproudbot.plugins.redmine_models import RedmineUser, ProjectChannel


logging = logging.getLogger(__name__)


@listen_to('[t](\d+)')
def show_ticket_information(message, ticket_id):
    """Redmineのチケット情報を参照する.

    :param message: slackbotの各種パラメータを保持したclass
    :param ticket_id: redmineのチケット番号
    """
    s = Session()

    channel = message.channel
    channel_id = channel._body['id']
    user_id = message.body['user']
    user = s.query(RedmineUser).filter(RedmineUser.user_id == user_id).first()

    if not user:
        user_name = get_user_name(user_id)
        message.send('{}は登録されていません。'.format(user_name))
        return
        
    url = "https://project.beproud.jp/redmine/issues/{}".format(ticket_id)
    headers = {'X-Redmine-API-Key': user.api_key}
    res = requests.get("{}.json".format(url), headers=headers)

    if res.status_code == 200:
        ticket = res.json()

        proj_id = ticket["issue"]["project"]["id"]
        proj_room = s.query(ProjectChannel).filter(ProjectChannel.id == proj_id ).first()

        if proj_room and channel_id in proj_room.rooms.split(","):
            message.send("{} {}".format(ticket["issue"]["subject"], url))
        else:
            message.send("{}は{}で表示できません。".format(ticket_id, channel._body['name']))
    else:
        user_name = get_user_name(user_id)
        logging.info("{} doesn't have access to ticket #{}".format(user_name, ticket_id))

