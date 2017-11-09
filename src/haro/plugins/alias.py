from prettytable import PrettyTable
from slackbot.bot import respond_to

from db import Session
from haro.plugins.alias_models import UserAliasName
from haro.slack import get_user_name, get_slack_id_by_name

HELP = """
- `$alias show [user_name]`: Slackのユーザーに紐づいているエイリアス名一覧を表示する
- `$alias add [user_name] <alias_name>`: Slackのユーザーに紐づくエイリアス名を登録する
- `$alias del [user_name] <alias_name>`: Slackのユーザーに紐づくエイリアス名を削除する
- `$alias help`: aliasコマンドの使い方を返す
- ※各コマンドにてuser_name引数を省略した際には投稿者に対しての操作になります
"""


@respond_to('^alias\s+show$')
@respond_to('^alias\s+show\s+(\S+)$')
def show_user_alias_name(message, user_name=None):
    """ユーザーのエイリアス名一覧を表示する

    :param message: slackbotの各種パラメータを保持したclass
    :param str user: Slackのユーザー名
    """
    if user_name:
        slack_id = get_slack_id_by_name(user_name)
    else:
        slack_id = message.body['user']
        user_name = get_user_name(slack_id)

    if not slack_id:
        message.send('{}に紐づくSlackのuser_idは存在しません'.format(user_name))
        return

    s = Session()
    alias_names = [user.alias_name for user in
                   s.query(UserAliasName)
                   .filter(UserAliasName.slack_id == slack_id)]

    pt = PrettyTable(['ユーザー名', 'Slack ID', 'エイリアス名'])
    alias_name = ','.join(alias_names)
    pt.add_row([user_name, slack_id, alias_name])
    message.send('```{}```'.format(pt))


@respond_to('^alias\s+add\s+(\S+)$')
@respond_to('^alias\s+add\s+(\S+)\s+(\S+)$')
def alias_name(message, user_name, alias_name=None):
    """指定したユーザにエイリアス名を紐付ける

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: エイリアス名を紐付けるSlackユーザー
    :param str alias_name: Slackユーザーに紐付けるエイリアス名
       alias_nameがNoneの場合、user_nameをalias_nameとして扱う
       上記の場合user_nameは投稿者となる
    """
    if alias_name:
        # ユーザー名とエイリアス名が指定されているパターン
        slack_id = get_slack_id_by_name(user_name)
    else:
        # 投稿者のエイリアス名を更新するパターン
        alias_name = user_name
        slack_id = message.body['user']
        user_name = get_user_name(slack_id)

    user = get_slack_id_by_name(alias_name)
    if user:
        message.send('`{}` はユーザーが存在しているので使用できません'.format(alias_name))
        return

    if not slack_id:
        message.send('{}に紐づくSlackのuser_idは存在しません'.format(user_name))
        return

    s = Session()
    alias_user_name = (s.query(UserAliasName)
                       .filter(UserAliasName.alias_name == alias_name))
    if s.query(alias_user_name.exists()).scalar():
        message.send('エイリアス名 `{}` は既に登録されています'.format(alias_name))
        return

    s.add(UserAliasName(slack_id=slack_id, alias_name=alias_name))
    s.commit()
    message.send('{}のエイリアス名に `{}` を追加しました'.format(user_name, alias_name))


@respond_to('^alias\s+del\s+(\S+)$')
@respond_to('^alias\s+del\s+(\S+)\s+(\S+)$')
def unalias_name(message, user_name, alias_name=None):
    """ユーザーに紐づくエイリアス名を削除する

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: 削除するエイリアス名を持つSlackユーザー
    :param str alias_name: 削除するエイリアス名
       alias_nameがNoneの場合、user_nameをalias_nameとして扱う
       上記の場合user_nameは投稿者となる
    """
    if alias_name:
        # ユーザー名とエイリアス名が指定されているパターン
        slack_id = get_slack_id_by_name(user_name)
    else:
        # 投稿者のエイリアス名を更新するパターン
        alias_name = user_name
        slack_id = message.body['user']
        user_name = get_user_name(slack_id)

    if not slack_id:
        message.send('{}に紐づくSlackのuser_idは存在しません'.format(user_name))
        return

    s = Session()
    alias_user_name = (s.query(UserAliasName)
                       .filter(UserAliasName.slack_id == slack_id)
                       .filter(UserAliasName.alias_name == alias_name)
                       .one_or_none())

    if alias_user_name:
        s.delete(alias_user_name)
        s.commit()
        message.send('{}のエイリアス名から `{}` を削除しました'.format(user_name, alias_name))
    else:
        message.send('{}のエイリアス名 `{}` は登録されていません'.format(user_name, alias_name))


@respond_to('^alias\s+help$')
def show_help_alias_commands(message):
    """Userコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
