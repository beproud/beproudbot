from random import choice
from textwrap import dedent
from slackbot.bot import respond_to
from sqlalchemy import func
from db import Session
from utils import get_user_name
from beproudbot.plugins.redbull_models import RedbullHistory

# ランダムな文字列生成する為、定義
ALLOWED_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

_cache = {'token': None}


@respond_to('^redbull\s+count$')
def count_redbull_stock(message):
    """現在のRedBullの在庫本数を返すコマンド
    """
    s = Session()
    q = s.query(func.sum(RedbullHistory.delta).label('total_delta'))
    total_delta = q.one().total_delta
    if total_delta is None:
        total_delta = 0
    message.send('レッドブル残り %s 本' % total_delta)


@respond_to('^redbull\s+([-]?[0-9]+)$')
def manage_redbull_stock(message, delta):
    """RedBullの本数の増減を行うコマンド

    :param str delta: POSTされた増減する本数
    """
    delta = -int(delta)
    user_name = get_user_name(message.body['user'])

    s = Session()
    s.add(RedbullHistory(who=user_name, delta=delta))
    s.commit()

    if delta > 0:
        message.send('レッドブルが%sにより%s本投入されました'
                     % (user_name, delta))
    else:
        message.send('レッドブルが%sにより%s本消費されました'
                     % (user_name, -delta))


@respond_to('^redbull\s+history$')
def show_redbull_user_history(message):
    """RedBullのUserごとの消費履歴を返すコマンド
    """
    user_name = get_user_name(message.body['user'])
    s = Session()
    qs = (s.query(RedbullHistory)
          .filter(RedbullHistory.who == user_name,
                  RedbullHistory.delta < 0)
          .order_by(RedbullHistory.id.asc()))
    tmp = []
    for line in qs:
        _created_at = line.created_at.strftime('%Y年%m月%d日 %H:%M:%S')
        tmp.append('[%s]  %s本' % (_created_at, -line.delta))

    ret = '消費履歴はありません'
    if tmp:
        ret = '\n'.join(tmp)

    message.send('%sの消費したレッドブル:\n%s' % (user_name, ret))


@respond_to('^redbull\s+clear$')
def confirm_clear_redbull(message):
    """RedBullの履歴データを削除する為のトークンを返すコマンド
    """
    _cache['token'] = ''.join(choice(ALLOWED_CHARS) for i in range(16))
    message.send('履歴をDBからすべてクリアします。'
                 '続けるには\n$redbull clear %s\nと書いてください'
                 % _cache['token'])


@respond_to('^redbull\s+clear\s+([a-zA-Z]+)$')
def clear_redbull(message, token):
    """RedBullの履歴データの削除コマンド
    POSTされたトークンが正しい場合に実行

    :param str token: `$redbull clear` の後に入力されたトークン
    """
    if token == _cache['token']:
        s = Session()
        s.query(RedbullHistory).delete()
        s.commit()
        message.send('履歴をクリアしました')
    else:
        message.send('コマンドが一致しないため'
                     '履歴をクリアできませんでした')


@respond_to('^redbull$')
def show_help_redbull_commands(message):
    """RedBullコマンドのhelpを表示
    """
    help_text = dedent('''\
    ```
    $redbull count        : RedBullの残り本数を表示する
    $redbull (num)        : numの数だけredbullの本数を減らす
    $redbull -(num)       : numの数だけredbullの本数を増やす
    $redbull history      : 自分のredbullの消費履歴を表示する
    $redbull clear        : RedBullのDBデータを削除する為の認証tokenを表示する
    $redbull clear token  : tokenが合っていればRedBullのDBデータを削除する
    ```''')
    message.send(help_text)
