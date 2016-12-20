import re
import csv
from io import StringIO
from itertools import groupby

import requests
from slackbot import settings
from slackbot.bot import respond_to, listen_to

from db import Session
from utils.slack import get_user_name
from beproudbot.plugins.kintai_models import KintaiHistory


HELP = """
- `$勤怠`: 自分の勤怠一覧を40日分表示する
- `$勤怠 export <month>`: monthに指定した月の勤怠記録をCSV形式で返す(defaultは当月)
- `$勤怠 help`: 勤怠コマンドの使い方を返す
- `$出社 <target_day> <workon_time>`: target_dayの出社時間をworkon_timeで登録します
- `$退社 <target_day> <workoff_time>`: target_dayの退社時間をworkon_timeで登録します
- `おはよう`、`お早う`, `出社しました`: 出社時間を記録します
- `帰ります`、`かえります`、`退社します`: 退社時間を記録します
"""


@listen_to('おはよう|お早う|出社しました')
def register_workon_time(message):
    """出社時間を記録して挨拶を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_name = get_user_name(message.body['user'])

    s = Session()
    s.add(KintaiHistory(who=user_name))
    s.commit()

    message.reply('おはようございます')


@listen_to('帰ります|かえります|退社します')
def register_workoff_time(message):
    """退社時間を記録して挨拶を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_name = get_user_name(message.body['user'])

    s = Session()
    s.add(KintaiHistory(who=user_name, is_workon=False))
    s.commit()

    message.reply('お疲れ様でした')


@respond_to('勤怠')
def show_kintai_history(message):
    """40日分の勤怠記録を表示します

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_name = get_user_name(message.body['user'])

    s = Session()
    qs = (s.query(KintaiHistory)
          .filter(KintaiHistory.who == user_name)
          .order_by(RedbullHistory.id.desc()))

@respond_to('^勤怠\s+help$')
def show_help_kintai_commands(message):
    """勤怠コマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
