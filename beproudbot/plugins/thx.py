from prettytable import PrettyTable
from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id_by_name
from db import Session
from beproudbot.plugins.thx_models import ThxHistory

HELP = """
- `$[user_name]++ [word]`: 指定したSlackのユーザーにGJする
- `$thx [user_name] <num>`: 最近num件(default 10)のGJの履歴を表示する
- `$thx [user_name] from`: 誰からGJされたかの一覧を表示する
- `$thx [user_name] to`: 誰にGJしたかの一覧を返す
- `$thx help`: thxコマンドの使い方を返す
"""


@respond_to('^thx\s+help$')
def show_help_thx_commands(message):
    """thxコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    message.send(HELP)


@respond_to('^(\S*[^\+])\+\+\s+(\S+)$')
def thx(message, user_name, word):
    """指定したSlackのユーザーにGJを行う

    :param message: slackbot.dispatcher.Message
    :param str user_name:
    :param str word:
    """
    pass


@respond_to('^thx\s+(\S+)\s+(\d+)$')
def show_thx_history(message, user_name, num=10):
    """GJの履歴を表示する

    :param message: slackbot.dispatcher.Message
    :param str user_name:
    :param str num:
    """
    pass


@respond_to('^thx\s+(\S+)\s+from$')
def show_thx_from(message, user_name):
    """誰からGJされたか表示します

    :param message: slackbot.dispatcher.Message
    :param str user_name:
    """
    pass


@respond_to('^thx\s+(\S+)\s+to$')
def show_thx_to(message, user_name):
    """誰にGJしたか表示します

    :param message: slackbot.dispatcher.Message
    :param str user_name:
    """
    pass
