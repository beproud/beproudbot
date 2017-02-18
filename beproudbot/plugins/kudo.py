from prettytable import PrettyTable
from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id
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
def update_kudo(message, name, action):
    """ 指定された名前に対して ++ または -- する

    OK:
       $name++、$name ++、$name  ++
    NG:
       $name---、$name ---、$name-++

    :param message: slackbot.dispatcher.Message
    :param name str: ++ または -- をする対象の名前
    :param action str: ++を指定した場合+1、--を指定した場合-1
    """
    slack_id = message.body['user']
    delta = 1 if action == '++' else -1

    s = Session()
    kudo = (s.query(KudoHistory)
            .filter(KudoHistory.name == name)
            .filter(KudoHistory.from_user_id == slack_id)
            .one_or_none())

    if kudo is None:
        s.add(KudoHistory(name=name, from_user_id=slack_id, delta=delta))
        s.commit()
    else:
        kudo.delta = kudo.delta + delta
        s.commit()


@respond_to('^kudo\s+rank_to\s+(\S+)$')
def show_kudo_rank_to(message, user_name):
    """nameが++/--した対象をRanking形式で表示する
    """
    slack_id = get_slack_id(s, user_name)
    s = Session()
    kudo = (s.query(KudoHistory)
            .filter(KudoHistory.from_user_id == slack_id)
            .order_by(KudoHistory.desc.desc()))

    msg = ['{}からの評価'.format(slack_id)]
    if kudo:
        rank_list = [(k.name, k.delta) for k in kudo]
        upper = rank_list[:20]
        lower = rank_list[-20:]
        for rank in upper:
            msg.append('{} : {}' % rank)
        msg.append('~' * 30)
        for rank in lower:
            msg.append('{} : {}' % rank)


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
