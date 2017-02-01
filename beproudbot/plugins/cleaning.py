from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id_by_name
from db import Session
from beproudbot.plugins.alias_models import UserAliasName
from beproudbot.plugins.cleaning_models import Cleaning, CleaningTask


HELP = """
- `$cleaning list`: 掃除当番の一覧を表示する
- `$cleaning today`: 今日の掃除当番を表示する
- `$cleaning <day_of_week>`: 指定された曜日の掃除当番を表示する
- `$cleaning add <user_name> <day_of_week>`: 掃除当番を追加する
- `$cleaning del <user_name> <day_of_week>`: 掃除当番から削除する
- `$cleaning swap <user_name> <user_name>`: 掃除当番を入れ替える
- `$cleaning move <user_name> <day_of_week>`: 掃除当番の曜日を入れ替える
- `$cleaning task`: 掃除の作業内容を表示する
- `$cleaning add task <task_name>` 掃除の作業内容を追加する
- `$cleaning del task <task_name>` 掃除の作業内容を削除する
- `$cleaning help`: cleaningコマンドの使い方を返す
"""


@respond_to('^cleaning\s+help$')
def show_help_cleaning_commands(message):
    """Cleaningコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)


@respond_to('^cleaning\s+today$')
@respond_to('^cleaning\s+(\S+)$')
def show_today_cleaning_duty(message, day_of_week=None):
    """曜日を指定して掃除当番を表示する

    :param message: slackbotの各種パラメータを保持したclass
    :param str day_of_week: 掃除当番を表示する曜日
    """
    pass


@respond_to('^cleaning\s+add\s+(\S+)\s+(\S+)$')
def cleaning_add(message, user_name, day_of_week):
    """指定した曜日の掃除当番にユーザーを追加する

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: 掃除当番に追加するユーザー名
    :param str day_of_week: 追加する掃除曜日
    """
    pass


@respond_to('^cleaning\s+del\s+(\S+)\s+(\S+)$')
def cleaning_del(message, user_name, day_of_week):
    """指定した曜日の掃除当番からユーザーを削除する

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: 掃除当番から削除するユーザー名
    :param str day_of_week: 削除する掃除曜日
    """
    pass


@respond_to('^cleaning\s+swap\s+(\S+)\s+(\S+)$')
def cleaning_swap(message, user_name1, user_name2):
    """登録された掃除当番のユーザーの掃除曜日を入れ替える

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name1: 掃除当番の曜日を交換するユーザー名
    :param str user_name2: 掃除当番の曜日を交換するユーザー名
    """
    pass


@respond_to('^cleaning\s+move\s+(\S+)\s+(\S+)$')
def cleaning_move(message, user_name, day_of_week):
    """登録された掃除当番のユーザーの掃除曜日を移動させる

    :param message: slackbotの各種パラメータを保持したclass
    :param str user_name: 掃除当番の曜日を移動させるユーザー名
    :param str day_of_week: 移動対象の曜日名
    """
    pass


@respond_to('^cleaning\s+task$')
def show_cleaning_task(message):
    """登録されている掃除作業を一覧表示する

    :param message: slackbotの各種パラメータを保持したclass
    """
    pass


@respond_to('^cleaning\s+task\s+add\s+(\S+)$')
def add_cleaning_task(message, task):
    """掃除作業を追加する

    :param message: slackbotの各種パラメータを保持したclass
    :param task: 登録する掃除作業
    """
    pass


@respond_to('^cleaning\s+task\s+del\s+(\S+)$')
def del_cleaning_task(message, task):
    """掃除作業を削除する

    :param message: slackbotの各種パラメータを保持したclass
    :param task: 削除する掃除作業
    """
    pass
