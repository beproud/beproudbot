from slackbot.bot import respond_to

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
