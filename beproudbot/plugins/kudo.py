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


@respond_to('^(\S*[^\+|\-|\s])\s*(\+\+|\-\-)$')
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
        message.send('({}: 通算 {})'.format(name, delta))
    else:
        kudo.delta = kudo.delta + delta
        s.commit()
        message.send('({}: 通算 {})'.format(kudo.name, kudo.delta))


@respond_to('^kudo\s+rank_to\s+(\S+)$')
def show_kudo_rank_to(message, user_name):
    """nameが++/--した対象をRanking形式で表示する
    """
    slack_id = get_slack_id_by_name(user_name)
    s = Session()
    kudo = (s.query(KudoHistory)
            .filter(KudoHistory.from_user_id == slack_id)
            .order_by(KudoHistory.delta.desc()))

    msg = ['{}からの評価'.format(user_name)]
    if kudo:
        rank_list = [(k.name, k.delta) for k in kudo]
        upper = rank_list[:20]
        lower = rank_list[-20:]
        for name, delta in upper:
            msg.append('{} : {}'.format(name, delta))
        msg.append('~' * 30)
        for name, delta in lower:
            msg.append('{} : {}'.format(name, delta))
        message.send('\n'.join(msg))
    else:
        message.send('{}が++/--した記録はありません'.format(user_name))


@respond_to('^kudo\s+rank_from\s+(\S+)$')
def show_kudo_rank_from(message, name):
    """nameが++/--された対象をRanking形式で表示する
    """
    s = Session()
    kudo = (s.query(KudoHistory)
            .filter(KudoHistory.name == name)
            .order_by(KudoHistory.delta.desc()))

    msg = ['{}への評価'.format(name)]
    if kudo:
        rank_list = [(get_user_name(k.from_user_id), k.delta) for k in kudo]
        upper = rank_list[:20]
        lower = rank_list[-20:]
        for user_name, delta in upper:
            msg.append('{} : {}'.format(user_name, delta))
        msg.append('~' * 30)
        for user_name, delta in lower:
            msg.append('{} : {}'.format(user_name, delta))
        message.send('\n'.join(msg))
    else:
        message.send('{}が++/--された記録はありません'.format(name))


@respond_to('^kudo\s+help$')
def show_help_alias_commands(message):
    """Kudoコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
