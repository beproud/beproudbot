from collections import OrderedDict

from prettytable import PrettyTable
from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id_by_name
from db import Session
from beproudbot.plugins.user_models import UserAliasName

HELP = """
- `$user list`: Slackのユーザー情報を一覧表示
- `$user alias <user_name> <alias_name>`: Slackのユーザーに指定したエイリアス名を紐づける
- `$user unalias <user_name> <alias_name>`: Slackのユーザーから指定したエイリアス名との紐付けを解除する
- `$user help`: userコマンドの使い方を返す
"""


@respond_to('^user\s+list$')
def show_user_list(message):
    """User一覧を表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    users = OrderedDict()
    pt = PrettyTable(['user_name', 'slack_id', 'alias_name'])
    s = Session()
    for q in s.query(UserAliasName).order_by(UserAliasName.slack_id):
        users.setdefault(q.slack_id, []).append(q.alias_name)

    for slack_id, alias_names in users.items():
        user_name = get_user_name(slack_id)
        alias_name = ','.join(alias_names)
        pt.add_row([user_name, slack_id, alias_name])

    message.send('```{}```'.format(pt))


@respond_to('^user\s+alias\s(.*)\s(.*)$')
def alias_name(message, user_name, alias_name):
    """指定したユーザにエイリアス名を紐付ける

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: エイリアス名を紐付けるSlackユーザー
    :param str alias_name: Slackユーザーに紐付けるエイリアス名
    """
    slack_id = get_slack_id_by_name(user_name)
    if not slack_id:
        message.send('{}に紐づくSlackのuser_idは存在しません'.format(user_name))
        return

    s = Session()
    alias_user_name = s.query(UserAliasName).filter(UserAliasName.alias_name == alias_name)
    if s.query(alias_user_name.exists()).scalar():
        message.send('エイリアス名 `{}` は既に登録されています'.format(alias_name))
        return

    s.add(UserAliasName(slack_id=slack_id, alias_name=alias_name))
    s.commit()
    message.send('{}のエイリアス名に `{}` を追加しました'.format(user_name, alias_name))


@respond_to('^user\s+unalias\s(.*)\s(.*)$')
def unalias_name(message, user_name, alias_name):
    """ユーザーに紐づくエイリアス名を削除する

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: 削除するエイリアス名を持つSlackユーザー
    :param str alias_name: 削除するエイリアス名
    """
    slack_id = get_slack_id_by_name(user_name)
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


@respond_to('^user\s+help$')
def show_help_user_commands(message):
    """Userコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
