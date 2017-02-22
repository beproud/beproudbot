from slackbot.bot import respond_to
from utils.slack import get_user_name
from utils.alias import get_slack_id
from db import Session
from beproudbot.plugins.kudo_models import KudoHistory

HELP = """
- `$<name>++`: 指定された名前に対して +1 します
- `$<name>--`: 指定された名前に対して -1 します
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
        # name ×from_user_id の組み合わせが存在していない -> 追加
        s.add(KudoHistory(name=name, from_user_id=slack_id, delta=delta))
        s.commit()
        message.send('({}: 通算 {})'.format(name, delta))
    else:
        # name ×from_user_id の組み合わせが存在 -> 更新
        kudo.delta = kudo.delta + delta
        s.commit()
        message.send('({}: 通算 {})'.format(kudo.name, kudo.delta))


@respond_to('^kudo\s+rank_to\s+(\S+)$')
def show_kudo_rank_to(message, user_name):
    """指定したユーザーが++/--した対象をRanking形式で表示する

    :param message: slackbot.dispatcher.Message
    :param str user_name: ++/--を行ったユーザー名
    """
    slack_id = get_slack_id(user_name)
    if not slack_id:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    s = Session()
    kudo = (s.query(KudoHistory)
            .filter(KudoHistory.from_user_id == slack_id)
            .order_by(KudoHistory.delta.desc()))

    if kudo:
        msg = ['{}からの評価'.format(user_name)]
        for k in kudo:
            msg.append('{:+d} : {}'.format(k.delta, k.name))
        message.send('\n'.join(msg))
    else:
        message.send('{}が++/--した記録はありません'.format(user_name))


@respond_to('^kudo\s+rank_from\s+(\S+)$')
def show_kudo_rank_from(message, name):
    """指定したユーザーが++/--された対象をRanking形式で表示する

    :param message: slackbot.dispatcher.Message
    :param str name: ++/--された対象名
    """
    s = Session()
    kudo = (s.query(KudoHistory)
            .filter(KudoHistory.name == name)
            .order_by(KudoHistory.delta.desc()))

    msg = ['{}への評価'.format(name)]
    if kudo:
        rank_list = [(k.delta, get_user_name(k.from_user_id)) for k in kudo]
        if len(rank_list) > 40:
            upper = rank_list[:20]
            lower = rank_list[-20:]
            for user_name, delta in upper:
                msg.append('{:+d} : {}'.format(delta, user_name))
            msg.append('~' * 30)
            for user_name, delta in lower:
                msg.append('{:+d} : {}'.format(delta, user_name))
        else:
            for user_name, delta in rank_list:
                msg.append('{:+d} : {}'.format(delta, user_name))
        message.send('\n'.join(msg))
    else:
        message.send('{}が++/--された記録はありません'.format(name))


@respond_to('^kudo\s+help$')
def show_help_alias_commands(message):
    """Kudoコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
