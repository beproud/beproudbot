from slackbot.bot import respond_to
from sqlalchemy import func

from db import Session
from utils.slack import get_user_name
from beproudbot.plugins.water_models import WaterHistory

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
    q = s.query(func.sum(WaterHistory.delta).label('total_delta'))
    total_delta = q.one().total_delta
    latest = (s.query(WaterHistory)
              .filter(WaterHistory.delta > 0)
              .order_by(WaterHistory.id.desc())).first()

    created_at = latest.created_at.strftime('%Y年%m月%d日')

    if total_delta is None:
        total_delta = 0
    message.send('残数: {}本 ({} 追加)'.format(total_delta, created_at))


@respond_to('^water\s+([-]?[0-9]+)$')
def manage_water_stock(message, delta):
    """水の本数の増減を行うコマンド

    :param message: slackbotの各種パラメータを保持したclass
    :param str delta: POSTされた増減する本数
    """
    delta = -int(delta)
    user_name = get_user_name(message.body['user'])

    s = Session()
    s.add(WaterHistory(who=user_name, delta=delta))
    s.commit()

    q = s.query(func.sum(WaterHistory.delta).label('total_delta'))
    total_delta = q.one().total_delta

    if delta > 0:
        message.send('ウォーターサーバーのボトルが{}本追加されました。(残数: {}本)'
                     .format(delta, total_delta))
    else:
        message.send('ウォーターサーバーのボトルを{}本取りかえました。(残数: {}本)'
                     .format(delta, total_delta))


@respond_to('^water\s+history(\s+[0-9])?$')
def show_water_history(message, limit):
    """水の管理履歴を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    v = 10
    if limit is not None:
        v = limit
    s = Session()
    qs = (s.query(WaterHistory)
          .order_by(WaterHistory.id.asc())
          .limit(v))

    tmp = []
    for line in qs:
        created_at = line.created_at.strftime('%Y年%m月%d日')
        if line.delta > 0:
            tmp.append('[{}]  {}本 追加'.format(created_at, line.delta))
        else:
            tmp.append('[{}]  {}本 取替'.format(created_at, -line.delta))

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
