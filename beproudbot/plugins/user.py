from prettytable import PrettyTable

from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id_by_name
from db import Session
from beproudbot.plugins.user_models import User, UserAliasName

HELP = """
- `$user list`: Slackのユーザー情報を一覧表示
- `$user add <user_name>`: 指定したユーザー名のSlackのuser_idを追加
- `$user del <slack_user_id>`: 指定したSlackのuser_idを削除
- `$user alias <alias_name> <user_name>`: 指定したエイリアス名をユーザー名に紐付ける
- `$user unalias <alias_name> <user_name>`: 指定したエイリアス名とユーザー名の紐付けを解除する
- `$user slack_id <user_name>`: 指定したユーザー名のSlackのuser_idを返します
- `$user help`: userコマンドの使い方を返す
"""


@respond_to('^user\s+help$')
def show_help_user_commands(message):
    """Userコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)


@respond_to('^user\s+list$')
def show_user_list(message):
    """User一覧を表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    pt = PrettyTable(['user_name', 'user_id', 'alias_name'])
    s = Session()
    for q in s.query(User).all():
        user_id = q.slack_id
        user_name = get_user_name(user_id)
        alias_names = ','.join([i.alias_name for i in q.user_name_alias])
        pt.add_row([user_name, user_id, alias_names])

    message.send('```{}```'.format(pt))


@respond_to('^user\s+add\s(.*)$')
def add_user_id(message, user_name):
    """Slackのuser_idをUserテーブルに追加

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: 登録するslackのユーザー名
    """
    user_id = get_slack_id_by_name(user_name)
    if not user_id:
        message.send('{}に紐づくSlackのuser_idは存在しません'.format(user_name))
        return

    s = Session()
    user = s.query(User).filter(User.slack_id == user_id).one_or_none()
    if user:
        message.send('{}は既に登録されています'.format(user_name))
    else:
        s.add(User(slack_id=user_id))
        s.commit()
        message.send('{}のuser_idを追加しました'.format(user_name))


@respond_to('^user\s+del\s(.*)$')
def delete_user_id(message, user_name):
    """Slackのuser_idをUserテーブルから削除

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: 削除するslackのユーザー名
    """
    user_id = get_slack_id_by_name(user_name)
    if not user_id:
        message.send('{}に紐づくSlackのuser_idは存在しません'.format(user_name))
        return

    s = Session()
    user = s.query(User).filter(User.slack_id == user_id).one_or_none()
    if user:
        s.delete(user)
        s.commit()
        message.send('{}のuser_idを削除しました'.format(user_name))
    else:
        message.send('{}は登録されていません'.format(user_name))


@respond_to('^user\s+alias\s(.*)\s(.*)$')
def alias_user_name(message, alias_name, user_name):
    """エイリアス名をユーザー名に紐付ける

    :param message: slackbotの各種パラメータを保持したclass
    :param str alias_name: ユーザー名に紐付けるエイリアス名
    :param str user_name: エイリアス名を紐付けるユーザー名
    """
    user_id = get_slack_id_by_name(user_name)
    if not user_id:
        message.send('{}に紐づくSlackのuser_idは存在しません'.format(user_name))
        return

    s = Session()
    alias_user_name = s.query(UserAliasName).filter(UserAliasName.alias_name == alias_name)
    if s.query(alias_user_name.exists()).scalar():
        message.send('エイリアス名 `{}` は既に登録されています'.format(alias_name))
        return

    user = s.query(User).filter(User.slack_id == user_id).one_or_none()
    if user:
        s.add(UserAliasName(user=user.id, alias_name=alias_name))
        s.commit()
        message.send('{}のエイリアス名に `{}` を追加しました'.format(user_name, alias_name))
    else:
        message.send('{}はuserとして登録されていません'.format(user_name))


@respond_to('^user\s+unalias\s(.*)\s(.*)$')
def unalias_user_name(message, alias_name, user_name):
    """ユーザー名に紐づくエイリアス名を削除する

    :param message: slackbotの各種パラメータを保持したclass
    :param str alias_name: 削除するエイリアス名
    :param str user_name: 削除するエイリアス名を持つユーザー名
    """
    user_id = get_slack_id_by_name(user_name)
    if not user_id:
        message.send('{}に紐づくSlackのuser_idは存在しません'.format(user_name))
        return

    s = Session()
    alias_user_name = (s.query(UserAliasName).filter(UserAliasName.alias_name == alias_name))
    if not s.query(alias_user_name.exists()).scalar():
        message.send('エイリアス名 `{}` は登録されていません'.format(
            alias_name))
        return

    name = (s.query(UserAliasName)
            .select_from(User)
            .join(User.user_name_alias)
            .filter(User.slack_id == user_id)
            .filter(UserAliasName.alias_name == alias_name)
            .one_or_none())
    if name:
        s.delete(name)
        s.commit()
        message.send('{}のエイリアス名から `{}` を削除しました'.format(user_name, alias_name))
    else:
        message.send('{}のエイリアス名 `{}` は登録されていません'.format(user_name, alias_name))


@respond_to('^user\s+slack_id\s(.*)$')
def show_slack_id(message, user_name):
    """指定したユーザーのSlackのuser_idを返す

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: Slackのユーザー名
    """
    user_id = get_slack_id_by_name(user_name)
    if user_id:
        message.send('{}のSlackのuser_idは `{}` です'.format(user_name, user_id))
    else:
        message.send('{}のSlackのuser_idは存在しません'.format(user_name))
