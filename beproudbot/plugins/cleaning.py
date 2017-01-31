from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id_by_name
from db import Session
from beproudbot.plugins.cleaning_models import UserAliasName


HELP = """
- `$cleaning list`: 掃除当番の一覧を表示する
- `$cleaning today`: 今日の掃除当番を表示する
- `$cleaning add <user_name> <day_of_week>`: 掃除当番を追加する
- `$cleaning del <user_name> <day_of_week>`: 掃除当番から削除する
- `$cleaning <day_of_week>`: 指定された曜日の掃除当番を表示する
- `$cleaning swap <user_name> <user_name>`: 掃除当番を入れ替える
- `$cleaning move <user_name> <day_of_week>`: 掃除当番の曜日を入れ替える
- `$cleaning help`: 掃除の内容を表示する
"""


@respond_to('^cleaning\s+help$')
def show_help_alias_commands(message):
    """Userコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
