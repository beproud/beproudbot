import csv
from io import StringIO
from string import ascii_letters
from random import choice
from itertools import groupby

import requests
from slackbot import settings
from slackbot.bot import respond_to
from sqlalchemy import func

from db import Session
from utils.slack import get_user_name
from beproudbot.plugins.redbull_models import RedbullHistory

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
    q = s.query(func.sum(RedbullHistory.delta).label('total_delta'))
    total_delta = q.one().total_delta
    if total_delta is None:
        total_delta = 0
    message.send('レッドブル残り {} 本'.format(total_delta))


@respond_to('^redbull\s+([-]?[0-9]+)$')
def manage_redbull_stock(message, delta):
    """RedBullの本数の増減を行うコマンド

    :param message: slackbotの各種パラメータを保持したclass
    :param str delta: POSTされた増減する本数
    """
    delta = -int(delta)
    user_name = get_user_name(message.body['user'])

    s = Session()
    s.add(RedbullHistory(who=user_name, delta=delta))
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
    user_name = get_user_name(message.body['user'])
    s = Session()
    qs = (s.query(RedbullHistory)
          .filter(RedbullHistory.who == user_name,
                  RedbullHistory.delta < 0)
          .order_by(RedbullHistory.id.asc()))
    tmp = []
    for line in qs:
        created_at = line.created_at.strftime('%Y年%m月%d日')
        tmp.append('[{}]  {}本'.format(created_at, -line.delta))

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
        return item.created_at.year, item.created_at.month

    ret = []
    for ((year, month), items) in groupby(consume_hisotry, grouper):
        count = -sum([int(item.delta) for item in items])
        ret.append([year + '/' + month, str(count)])

    output = StringIO()
    w = csv.writer(output, quoting=csv.QUOTE_ALL)
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
@respond_to('^redbull\s+clear\s+([a-zA-Z]+)$')
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
                     '続けるには\n$redbull clear {}\nと書いてください'
                     .format(_cache['token']))
        return

    if token == _cache['token']:
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
