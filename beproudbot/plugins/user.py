from slackbot.bot import respond_to
from db import Session
from beproudbot.plugins.user_models import User, UserNameAlias

HELP = """
- `$user list`: Slack ユーザーIDに紐づく名前を一覧表示
- `$user add <user_id>`: 指定したSlackのuser_idを追加
- `$user del <user_id>`: 指定したSlackのuser_idを削除
- `$user alias <username> <user_id>`: 指定したユーザー名をSlackのuser_idに紐付ける
- `$user unalias <username> <user_id>`: 指定したユーザー名をSlackのuser_idから紐付けを解除する
- `$user help`: userコマンドの使い方を返す
"""


@respond_to('^redbull\s+help$')
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
    # 出力はこんな感じ、※以下を使ってみたい
    # https://pypi.python.org/pypi/PrettyTable
    """
    ユーザー一覧
    slack_id: エイリアス名
    whogehoge: wan, wanshot, ワン
    xhogehoge: altnight, おるとにゃー
    """
    pass


@respond_to('^user\s+add\s(.*)$')
def add_user_id(message, slack_id):
    """user_idを追加

    :param message: slackbotの各種パラメータを保持したclass
    """
    s = Session()
    s.add(User(slack_id=slack_id))
    s.commit()
    user_id = message.body['user']
    message.send('{}'.format(user_id))


@respond_to('^user\s+alias\s(.*)\s(.*)$')
def add_user_alias(message, alias_name, slack_id):
    """user_idにuser_aliasを紐付ける

    :param message: slackbotの各種パラメータを保持したclass
    """
    s = Session()
    user = s.query(User).filter(User.slack_id == slack_id).one()
    s.add(UserNameAlias(user=user.id, alias_name=alias_name))
    s.commit()
