import random

from slackbot.bot import respond_to
from slackbot import settings
import slacker


HELP = '''- `$random`: チャンネルにいるメンバーからランダムに一人を選ぶ
- `$random active`: チャンネルにいるactiveなメンバーからランダムに一人を選ぶ
- `$random help`: randomコマンドの使い方を返す
'''

@respond_to('^random$')
@respond_to('^random\s+(active|help)$')
def random_command(message, subcommand=None):
    """
    チャンネルにいるメンバーからランダムに一人を選んで返す
    - https://github.com/os/slacker
    - https://api.slack.com/methods/channels.info
    - https://api.slack.com/methods/users.getPresence
    - https://api.slack.com/methods/users.info
    """

    if subcommand == 'help':
        message.send(HELP)
        return

    # チャンネルのメンバー一覧を取得
    channel = message.body['channel']
    webapi = slacker.Slacker(settings.API_TOKEN)
    cinfo = webapi.channels.info(channel)
    members = cinfo.body['channel']['members']

    # bot の id は除く
    bot_id = message._client.login_data['self']['id']
    members.remove(bot_id)

    member_id = None
    while not member_id:
        # メンバー一覧からランダムに選んで返す
        member_id = random.choice(members)
        if subcommand == 'active':
            # active が指定されている場合は presence を確認する
            presence = webapi.users.get_presence(member_id)
            if presence.body['presence'] == 'away':
                members.remove(member_id)
                member_id = None

    user_info = webapi.users.info(member_id)
    name = user_info.body['user']['name']
    message.send('{} さん、君に決めた！'.format(name))
