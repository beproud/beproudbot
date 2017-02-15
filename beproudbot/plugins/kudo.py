from prettytable import PrettyTable
from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id_by_name
from db import Session
from beproudbot.plugins.kudo_models import KudoHistory

HELP = """
- `$<name>++`: 指定された名前に対して +1 カウントします
- `$<name>--`: 指定された名前に対して -1 カウントします
- `$kudo rank_to <name>`: nameが++/--した対象をranking形式で表示する
- `$kudo rank_from <name>`: nameが++/--された対象をranking形式表示する
- `$kudo help`: kudoコマンドの使い方を返す
"""


@respond_to('^(\S*[^\+|\-])\s*(\+\+|\-\-)$')
def kudo(message, name, action):
    """ 指定された名前に対して ++ または -- する

    OK:
       $name++、$name ++、$name  ++
    NG:
       $name---、$name ---、$name-++

    :param message: slackbot.dispatcher.Message
    :param name str: ++ または -- をする対象の名前
    :param action str: ++を指定した場合+1、--を指定した場合-1
    """
    pass


@respond_to('^kudo\s+rank_to\s+(\S+)$')
def show_kudo_rank_to(message, name):
    """nameが++/--した対象をRanking形式で表示する
    """
    pass


@respond_to('^kudo\s+rank_from\s+(\S+)$')
def show_kudo_rank_from(message, name):
    """nameが++/--された対象をRanking形式で表示する
    """
    pass


@respond_to('^kudo\s+help$')
def show_help_alias_commands(message):
    """Kudoコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
