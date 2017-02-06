from prettytable import PrettyTable
from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id_by_name
from db import Session
from beproudbot.plugins.kudo_models import KudoHistory

HELP = """
- `$<name>++`: nameに++を行う
- `$<name>--`: nameに--を行う
- `$kudo rank <name>`: nameの
- `$kudo rank_to <name>`: nameが++/--した対象を一覧表示する
- `$kudo rank_from <name>`: nameが++/--された対象を一覧表示する
- `$kudo monthly <name> [month]`:
- `$kudo help`: kudoコマンドの使い方を返す
"""


@respond_to('^kudo\s+++$')
def kudo_plusplus(message):
    pass


@respond_to('^kudo\s+--$')
def kudo_minusminus(message):
    pass


@respond_to('^kudo\s+rank\s+(\S+)$')
def show_kudo_rank(message, name):
    pass


@respond_to('^kudo\s+rank_to\s+(\S+)$')
def show_kudo_rank_to(message, name):
    pass


@respond_to('^kudo\s+rank_from\s+(\S+)$')
def show_kudo_rank_from(message, name):
    pass


@respond_to('^kudo\s+monthly\s+(\S+)\s+(\S+)$')
def show_kudo_monthly_point(message, name):
    pass


@respond_to('^kudo\s+help$')
def show_help_alias_commands(message):
    """Kudoコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
