from slackbot.bot import respond_to
from sqlalchemy import func
from db import Session
from utils import get_user_name
from beproudbot.plugins.water_models import WaterHistory

HELP = '''\
- `$water count`: 現在の残数を返す
- `$water num`: 水を取り替えた時に使用。指定した数だけ残数を減らす
- `$water -num`: 水を受け取ったときに使用。指定した数だけ残数を増やす
- `$water history`: 過去10件分の履歴を返す
- `$water hitsory num`: 指定した件数分の履歴を返す
- `$water help`: このコマンドの使い方を返す
'''


@respond_to('^water\s+count$')
def count_water_stock(message):
    """現在の水の在庫本数を返すコマンド
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
    message.send('残数: %s本 (%s 追加)' % (total_delta, created_at))


@respond_to('^water\s+([-]?[0-9]+)$')
def manage_water_stock(message, delta):
    """水の本数の増減を行うコマンド

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
        message.send('ウォーターサーバーのボトルが%s本追加されました。(残数: %s本)'
                     % (delta, total_delta))
    else:
        message.send('ウォーターサーバーのボトルを%s本取りかえました。(残数: %s本)'
                     % (-delta, total_delta))


@respond_to('^water\s+history(\s+[0-9])?$')
def show_water_history(message, limit):
    """水の管理履歴を返すコマンド
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
            tmp.append('[%s]  %s本 追加' % (created_at, line.delta))
        else:
            tmp.append('[%s]  %s本 取替' % (created_at, -line.delta))

    ret = '管理履歴はありません'
    if tmp:
        ret = '\n'.join(tmp)

    message.send('水の管理履歴:\n%s' % ret)


@respond_to('^water\s+help$')
def show_help_water_commands(message):
    """waterコマンドのhelpを表示
    """
    message.send(HELP)
