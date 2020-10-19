from slackbot.bot import respond_to, listen_to
from sqlalchemy import func
from db import Session
from haro.botmessage import botsend
from haro.plugins.kudo_models import KudoHistory
from haro.slack import get_user_name

HELP = """
- `<name>++`: 指定された名称に対して++します
- `$kudo help`: kudoコマンドの使い方を返す
"""


@listen_to(r'^(.*)\s*(?<!\+)\+\+$')
def update_kudo(message, names):
    """ 指定された名前に対して ++ する

    OK:
       name++、name ++、name  ++、@name++、name1 name2++

    NG:
       name+ +、name++hoge、 name1,name2++


    :param message: slackbot.dispatcher.Message
    :param name str: ++する対象の名前
    """
    slack_id = message.body['user']
    name_list = []
    for name in [x for x in names.split(' ') if x]:
        # slackのsuggest機能でユーザーを++した場合(例: @wan++)、name引数は
        # `<@{slack_id}>` というstr型で渡ってくるので対応
        if get_user_name(name.lstrip('<@').rstrip('>')):
            name = get_user_name(name.lstrip('<@').rstrip('>'))

        s = Session()
        kudo = (s.query(KudoHistory)
                .filter(KudoHistory.name == name)
                .filter(KudoHistory.from_user_id == slack_id)
                .one_or_none())

        if kudo is None:
            # name ×from_user_id の組み合わせが存在していない -> 新規登録
            s.add(KudoHistory(name=name, from_user_id=slack_id, delta=1))
            s.commit()
        else:
            # name ×from_user_id の組み合わせが存在 -> 更新
            kudo.delta = kudo.delta + 1
            s.commit()

        q = (s.query(
            func.sum(KudoHistory.delta).label('total_count'))
            .filter(KudoHistory.name == name))
        total_count = q.one().total_count
        name_list.append((name, total_count))

    msg = ['({}: 通算 {})'.format(n, tc) for n, tc in name_list]
    botsend(message, '\n'.join(msg))


@respond_to(r'^kudo\s+help$')
def show_help_alias_commands(message):
    """Kudoコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    botsend(message, HELP)
