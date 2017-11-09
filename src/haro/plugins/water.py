import datetime

from slackbot.bot import respond_to
from sqlalchemy import func, case

from db import Session
from haro.plugins.water_models import WaterHistory

HELP = '''
- `$water count`: 現在の残数を返す
- `$water num`: 水を取り替えた時に使用。指定した数だけ残数を減らす(numが負数の場合、増やす)
- `$water hitsory <num>`: 指定した件数分の履歴を返す(default=10)
- `$water help`: このコマンドの使い方を返す
'''


@respond_to('^water\s+count$')
def count_water_stock(message):
    """現在の水の在庫本数を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    s = Session()
    stock_number, latest_ctime = (
        s.query(func.sum(WaterHistory.delta),
                func.max(case(whens=((
                    WaterHistory.delta > 0,
                    WaterHistory.ctime),), else_=None))).first()
    )

    if stock_number:
        latest_ctime = datetime.datetime.strptime(latest_ctime,
                                                  '%Y-%m-%d %H:%M:%S')
        message.send('残数: {}本 ({:%Y年%m月%d日} 追加)'
                     .format(stock_number, latest_ctime))
    else:
        message.send('管理履歴はありません')


@respond_to('^water\s+(-?\d+)$')
def manage_water_stock(message, delta):
    """水の本数の増減を行うコマンド

    :param message: slackbotの各種パラメータを保持したclass
    :param str delta: POSTされた増減する本数
        UserからPOSTされるdeltaの値は追加の場合は負数、取替の場合は正数
        DBは追加の場合正数、取替の場合は負数を記録する
    """
    delta = -int(delta)
    user_id = message.body['user']

    s = Session()
    s.add(WaterHistory(user_id=user_id, delta=delta))
    s.commit()

    q = s.query(func.sum(WaterHistory.delta).label('stock_number'))
    stock_number = q.one().stock_number

    if delta < 0:
        message.send('ウォーターサーバーのボトルを{}本取りかえました。(残数: {}本)'
                     .format(-delta, stock_number))
    else:
        message.send('ウォーターサーバーのボトルを{}本追加しました。(残数: {}本)'
                     .format(delta, stock_number))


@respond_to('^water\s+history$')
@respond_to('^water\s+history\s+(\d+)$')
def show_water_history(message, limit='10'):
    """水の管理履歴を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    s = Session()
    qs = (s.query(WaterHistory)
          .order_by(WaterHistory.id.desc())
          .limit(limit))

    tmp = []
    for line in qs:
        if line.delta > 0:
            tmp.append('[{:%Y年%m月%d日}]  {}本 追加'
                       .format(line.ctime, line.delta))
        else:
            tmp.append('[{:%Y年%m月%d日}]  {}本 取替'
                       .format(line.ctime, -line.delta))

    ret = '管理履歴はありません'
    if tmp:
        ret = '\n'.join(tmp)

    message.send('水の管理履歴:\n{}'.format(ret))


@respond_to('^water\s+help$')
def show_help_water_commands(message):
    """waterコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
