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


@listen_to('(.*)\s*\+\+\s+(\S+)')
def update_thx(message, user_names, word):
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

    s = Session()
    user_dict = check_user_name(s, user_names)

    msg = []
    if user_dict.get('matched'):
        for slack_id, user_name in user_dict['matched']:
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
            msg.append('{}({}: {}GJ)'.format(word, user_name, count))

    if user_dict.get('hint_name'):
        for hint_name in user_dict['hint_name']:
            msg.append('もしかして: `{}`'.format(hint_name))

    if user_dict.get('not_matched'):
        for name in user_dict['not_matched']:
            msg.append('{}はSlackのユーザーとして存在しません'.format(name))

    message.send('\n'.join(msg))


def check_user_name(session, user_names):
    """Slackユーザー情報と照ら合わせ結果を辞書で返す

    :param list user_names: Slackで＋＋対象のSlackユーザー名
    :return dict user_dict:
       keyが `matched`: Slackユーザーに紐付いた名前
       keyが `hint_name`: 紐付かなかったが、似た名前が存在する名前
       keyが `not_matched`: Slackユーザーに紐付かなかった名前
    """
    user_dict = {}
    for name in [x for x in user_names.split(' ') if x]:

        # slackのsuggest機能でユーザーを++した場合(例: @wan++)、name引数は
        # `<@{slack_id}>` というstr型で渡ってくるので対応
        if get_user_name(name.lstrip('<@').rstrip('>')):
            slack_id = name.lstrip('<@').rstrip('>')
        else:
            slack_id = get_slack_id(session, name)

        if slack_id:
            # slack_idに紐づくユーザーが存在
            user_dict.setdefault('matched', []).append((slack_id, name))
        else:
            # 一番近いユーザー名を算出
            hint = get_close_matches(name, get_users_info().values())
            if hint:
                user_dict.setdefault('hint_name', []).append(hint[0])
            # 紐づくユーザーが存在しなかった場合
            else:
                user_dict.setdefault('not_matched', []).append(name)
    return user_dict


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
