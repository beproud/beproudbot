import csv
from io import StringIO
from itertools import groupby
from random import choice
from string import ascii_letters

import requests
from slackbot import settings
from slackbot.bot import respond_to
from sqlalchemy import func
from db import Session
from haro.plugins.redbull_models import RedbullHistory
from haro.slack import get_user_name

_cache = {'token': None}

HELP = """
- `$redbull count`: RedBullの残り本数を表示する
- `$redbull num`: numの数だけRedBullの本数を減らす(負数の場合、増やす)
- `$redbull history`: 自分のRedBullの消費履歴を表示する
- `$redbull clear`: RedBullのDBデータを削除するtoken付きのコマンドを表示する
- `$redbull csv`: RedBullの月単位の消費履歴をCSV形式で表示する
- `$redbull help`: redbullコマンドの使い方を返す
"""


@respond_to('^redbull\s+count$')
def count_redbull_stock(message):
    """現在のRedBullの在庫本数を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    s = Session()
    q = s.query(func.sum(RedbullHistory.delta).label('stock_number'))
    stock_number = q.one().stock_number
    if stock_number is None:
        stock_number = 0
    message.send('レッドブル残り {} 本'.format(stock_number))


@respond_to('^redbull\s+(-?\d+)$')
def manage_redbull_stock(message, delta):
    """RedBullの本数の増減を行うコマンド

    :param message: slackbotの各種パラメータを保持したclass
    :param str delta: POSTされた増減する本数
        UserからPOSTされるdeltaの値は投入の場合は負数、消費の場合は正数
        DBは投入の場合正数、消費の場合は負数を記録する
    """
    delta = -int(delta)
    user_id = message.body['user']
    user_name = get_user_name(user_id)

    s = Session()
    s.add(RedbullHistory(user_id=user_id, delta=delta))
    s.commit()

    if delta > 0:
        message.send('レッドブルが{}により{}本投入されました'
                     .format(user_name, delta))
    else:
        message.send('レッドブルが{}により{}本消費されました'
                     .format(user_name, -delta))


@respond_to('^redbull\s+history$')
def show_user_redbull_history(message):
    """RedBullのUserごとの消費履歴を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_id = message.body['user']
    user_name = get_user_name(user_id)
    s = Session()
    qs = (s.query(RedbullHistory)
          .filter(RedbullHistory.user_id == user_id,
                  RedbullHistory.delta < 0)
          .order_by(RedbullHistory.id.asc()))
    tmp = []
    for line in qs:
        tmp.append('[{:%Y年%m月%d日}]  {}本'.format(line.ctime, -line.delta))

    ret = '消費履歴はありません'
    if tmp:
        ret = '\n'.join(tmp)

    message.send('{}の消費したレッドブル:\n{}'.format(user_name, ret))


@respond_to('^redbull\s+csv$')
def show_redbull_history_csv(message):
    """RedBullの月単位の消費履歴をCSVに出力する

    :param message: slackbotの各種パラメータを保持したclass
    """
    s = Session()
    consume_hisotry = (s.query(RedbullHistory)
                       .filter(RedbullHistory.delta < 0)
                       .order_by(RedbullHistory.id.desc()))

    # func.month関数を使って月ごとでgroupby count書けるが、
    # SQLiteにはMONTH()関数がないので月集計はPythonで処理する
    def grouper(item):
        return item.ctime.year, item.ctime.month

    ret = []
    for ((year, month), items) in groupby(consume_hisotry, grouper):
        count = -sum(item.delta for item in items)
        ret.append(['{}/{}'.format(year, month), str(count)])

    output = StringIO()
    w = csv.writer(output)
    w.writerows(ret)

    param = {
        'token': settings.API_TOKEN,
        'channels': message.body['channel'],
        'title': 'RedBull History Check'
    }
    requests.post(settings.FILE_UPLOAD_URL,
                  params=param,
                  files={'file': output.getvalue()})


@respond_to('^redbull\s+clear$')
@respond_to('^redbull\s+clear\s+(\w+)$')
def clear_redbull_history(message, token=None):
    """RedBullの履歴データを削除するコマンド

    `$redbull clear` のみだと削除するためのトークンを生成して表示する
    `$redbull clear <表示されたトークン>` をPOSTすると
        redbull_historyテーブルのレコード全削除を行う

    :param message: slackbotの各種パラメータを保持したclass
    :param str token: `$redbull clear` の後に入力されたトークン
    """
    if token is None:
        _cache['token'] = ''.join(choice(ascii_letters) for i in range(16))
        message.send('履歴をDBからすべてクリアします。'
                     '続けるには\n`$redbull clear {}`\nと書いてください'
                     .format(_cache['token']))
        return

    if token == _cache['token']:
        _cache['token'] = None
        s = Session()
        s.query(RedbullHistory).delete()
        s.commit()
        message.send('履歴をクリアしました')
    else:
        message.send('コマンドが一致しないため'
                     '履歴をクリアできませんでした')


@respond_to('^redbull\s+help$')
def show_help_redbull_commands(message):
    """RedBullコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
