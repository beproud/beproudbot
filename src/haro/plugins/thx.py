import re
import csv
from difflib import get_close_matches
from io import StringIO

import requests
from slackbot import settings
from slackbot.bot import respond_to, listen_to

from db import Session
from haro.plugins.thx_models import ThxHistory
from haro.slack import get_user_name, get_users_info
from haro.alias import get_slack_id

HELP = """
- `[user_name]++ [word]`: 指定したSlackのユーザーにGJする
- `$thx from <user_name>`: 誰からGJされたかの一覧を表示する
- `$thx to <user_name>`: 誰にGJしたかの一覧を返す
- `$thx help`: thxコマンドの使い方を返す
- ※各コマンドにてuser_name引数を省略した際には投稿者に対しての操作になります
"""


def find_thx(s, text):
    """Slackに投稿されたメッセージからthxを見つけて返す

    :param s: sqlalchemy.orm.session.Session
    :param str text: ユーザーが投稿した内容
    :return dict word_map_names_dict:
       キーがthx内容、バリューが対象Slackユーザーのリスト
    :return list hint_names: Slackユーザーに似た名前が存在する名前一覧
    :return list not_matched: Slackユーザーとして存在しなかった名前の一覧
    """
    word_map_names_dict = {}
    hint_names = []
    not_matched = []

    thx_matcher = re.compile('(?P<user_names>.+)[ \t\f\v]*\+\+[ \t\f\v]+(?P<word>.+)',
                             re.MULTILINE)
    for thx in thx_matcher.finditer(text):
        user_names = [x for x in thx.group('user_names').split(' ') if x]
        for name in user_names:
            if get_user_name(name.lstrip('<@').rstrip('>')):
                slack_id = name.lstrip('<@').rstrip('>')
            else:
                slack_id = get_slack_id(s, name)

            if slack_id:
                word_map_names_dict.setdefault(
                    thx.group('word'), []
                ).append((slack_id, name))
            else:
                # 一番近いユーザー名を算出
                hint = get_close_matches(name, get_users_info().values())
                if hint:
                    hint_names.append(hint[0])
                # 紐づくユーザーが存在しなかった場合
                else:
                    not_matched.append(name)

    return word_map_names_dict, hint_names, not_matched


@listen_to('.*\s*\+\+\s+.+')
def update_thx(message):
    """指定したSlackのユーザーにGJを行う

    OK:
       user_name++ hoge
       user_name ++ hoge
       user_name  ++ hoge
       @user_name++ hoge
       user_name user_name ++ hoge

    NG:
       user_name+ + hoge
       user_name+++ hoge
       user_name++hoge
       user_name,user_name ++ hoge

    :param message: slackbot.dispatcher.Message
    :param str user_name: ++するユーザー名
    :param str word: GJの内容
    """
    from_user_id = message.body['user']
    channel_id = message.body['channel']
    text = message.body['text']

    s = Session()
    user_dict, hint_names, not_matched = find_thx(s, text)

    msg = []
    if user_dict:
        for word, users in user_dict.items():
            for slack_id, name in users:
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
                msg.append('{}({}: {}GJ)'.format(word, name, count))

    if hint_names:
        for hint_name in hint_names:
            msg.append('もしかして: `{}`'.format(hint_name))

    if not_matched:
        for name in not_matched:
            msg.append('{}はSlackのユーザーとして存在しません'.format(name))

    message.send('\n'.join(msg))


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
                  files={'file': ("%s_thx.csv" % user_name, output.getvalue(), 'text/csv', )})


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
                  files={'file': ("%s_thx.csv" % user_name, output.getvalue(), 'text/csv',)})


@respond_to('^thx\s+help$')
def show_help_thx_commands(message):
    """thxコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    message.send(HELP)
