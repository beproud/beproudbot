import csv
from io import StringIO

import requests

from slackbot import settings
from slackbot.bot import respond_to, listen_to
from utils.slack import get_user_name
from utils.alias import get_slack_id
from db import Session
from beproudbot.plugins.thx_models import ThxHistory

HELP = """
- `[user_name]++ [word]`: 指定したSlackのユーザーにGJする
- `$thx from <user_name>`: 誰からGJされたかの一覧を表示する
- `$thx to <user_name>`: 誰にGJしたかの一覧を返す
- `$thx help`: thxコマンドの使い方を返す
- ※各コマンドにてuser_name引数を省略した際には投稿者に対しての操作になります
"""


@listen_to('^(\S*[^\+|\s])\s*\+\+\s+(\S+)$')
def update_thx(message, user_name, word):
    """指定したSlackのユーザーにGJを行う

    :param message: slackbot.dispatcher.Message
    :param str user_name: ++するユーザー名
    :param str word: GJの内容
    """
    from_user_id = message.body['user']
    channel_id = message.body['channel']

    s = Session()
    if user_name.startswith('<@') and get_user_name(user_name[2:11]):
        slack_id = user_name[2:11]
    else:
        slack_id = get_slack_id(s, user_name)

    if not slack_id:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    s.add(ThxHistory(
        user_id=slack_id,
        from_user_id=from_user_id,
        word=word,
        channel_id=channel_id))
    s.commit()

    count = (s.query(ThxHistory)
             .filter(ThxHistory.channel_id == channel_id)
             .filter(ThxHistory.user_id == slack_id)
             .count())
    message.send('{}({}: {}GJ)'.format(word, user_name, count))


@respond_to('^thx\s+from$')
@respond_to('^thx\s+from\s+(\S+)$')
def show_thx_from(message, user_name=None):
    """誰からGJされたか表示します

    :param message: slackbot.dispatcher.Message
    :param str user_name: GJされたユーザー名
    """
    channel_id = message.body['channel']
    s = Session()
    if not user_name:
        user_name = get_user_name(message.body['user'])
    slack_id = get_slack_id(s, user_name)
    if not slack_id:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    rows = [['GJしたユーザー', 'GJ内容']]
    thx = (s.query(ThxHistory)
            .filter(ThxHistory.user_id == slack_id)
            .filter(ThxHistory.channel_id == channel_id))

    for t in thx:
        rows.append([get_user_name(t.from_user_id), t.word])
    output = StringIO()
    w = csv.writer(output)
    w.writerows(rows)

    param = {
        'token': settings.API_TOKEN,
        'channels': channel_id,
        'title': '{}にGJした一覧'.format(user_name)
    }
    requests.post(settings.FILE_UPLOAD_URL,
                  params=param,
                  files={'file': output.getvalue()})


@respond_to('^thx\s+to$')
@respond_to('^thx\s+to\s+(\S+)$')
def show_thx_to(message, user_name=None):
    """誰にGJしたか表示します

    :param message: slackbot.dispatcher.Message
    :param str user_name:  GJしたユーザー名
    """
    channel_id = message.body['channel']
    if not user_name:
        user_name = get_user_name(message.body['user'])
    s = Session()
    slack_id = get_slack_id(s, user_name)
    if not slack_id:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    rows = [['GJされたユーザー', 'GJ内容']]
    thx = (s.query(ThxHistory)
            .filter(ThxHistory.from_user_id == slack_id)
            .filter(ThxHistory.channel_id == channel_id))
    for t in thx:
        rows.append([get_user_name(t.user_id), t.word])
    output = StringIO()
    w = csv.writer(output)
    w.writerows(rows)

    param = {
        'token': settings.API_TOKEN,
        'channels': channel_id,
        'title': '{}がGJした一覧'.format(user_name)
    }
    requests.post(settings.FILE_UPLOAD_URL,
                  params=param,
                  files={'file': output.getvalue()})


@respond_to('^thx\s+help$')
def show_help_thx_commands(message):
    """thxコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    message.send(HELP)
