import random

from slackbot.bot import respond_to
from slackbot import settings
import slacker


HELP = '''
- `$random`: チャンネルにいるメンバーからランダムに一人を選ぶ
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
    try:
        cinfo = webapi.channels.info(channel)
        members = cinfo.body['channel']['members']
    except slacker.Error:
        try:
            cinfo = webapi.groups.info(channel)
            members = cinfo.body['group']['members']
        except slacker.Error:
            # TODO: 例外で判定しないように修正する
            # チャンネルに紐付かない場合はreturn
            return

    # bot の id は除く
    bot_id = message._client.login_data['self']['id']
    members.remove(bot_id)

    member_id = None

    if subcommand != 'active':
        member_id = random.choice(members)
    else:
        # active が指定されている場合は presence を確認する
        random.shuffle(members)
        for member in members:
            presence = webapi.users.get_presence(member_id)
            if presence.body['presence'] == 'active':
                member_id = member
                break

    user_info = webapi.users.info(member_id)
    name = user_info.body['user']['name']
    message.send('{} さん、君に決めた！'.format(name))
