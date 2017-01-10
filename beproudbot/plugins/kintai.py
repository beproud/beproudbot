import csv
import datetime
from io import StringIO
from calendar import monthrange
from collections import defaultdict, OrderedDict

import requests
from slackbot import settings
from slackbot.bot import respond_to, listen_to
from sqlalchemy import func

from db import Session
from utils.slack import get_user_name

from beproudbot.plugins.kintai_models import KintaiHistory


HELP = """
- `$勤怠`: 自分の勤怠一覧を40日分表示する
- `$勤怠 csv <year>/<month>`: monthに指定した月の勤怠記録をCSV形式で返す(defaultは当年月)
- `おはよう`、`お早う`, `出社しました`: 出社時刻を記録します
- `帰ります`、`かえります`、`退社します`: 退社時刻を記録します
- `$勤怠 help`: 勤怠コマンドの使い方を返す
"""


DAY_OF_WEEK_MAP = {
    1: '月',
    2: '火',
    3: '水',
    4: '木',
    5: '金',
    6: '土',
    7: '日',
}


@listen_to('おはよう|お早う|出社しました')
def register_workon_time(message):
    """出社時刻を記録して挨拶を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_name = get_user_name(message.body['user'])

    s = Session()
    s.add(KintaiHistory(who=user_name))
    s.commit()

    message.reply('おはようございます')


@listen_to('帰ります|かえります|退社します')
def register_workoff_time(message):
    """退社時刻を記録して挨拶を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_name = get_user_name(message.body['user'])

    s = Session()
    s.add(KintaiHistory(who=user_name, is_workon=False))
    s.commit()

    message.reply('お疲れ様でした')


@respond_to('^勤怠$')
def show_kintai_history(message):
    """40日分の勤怠記録を表示します

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_name = get_user_name(message.body['user'])

    s = Session()
    qs = (s.query(KintaiHistory)
          .filter(KintaiHistory.who == user_name)
          .order_by(KintaiHistory.registered_at.desc())
          .limit(40))

    tmp = OrderedDict()
    for q in qs:
        day_of_week = DAY_OF_WEEK_MAP[q.registered_at.date().isoweekday()]
        prefix_day = '{:%Y年%m月%d日}({})'.format(q.registered_at,
                                                     day_of_week)
        registered_at = '{:%I:%M:%s}'.format(q.registered_at)
        kind = {0: '退社', 1: '出社'}.get(q.is_workon)
        tmp.setdefault(prefix_day, []).append('{}:{}'.format(kind,
                                                             registered_at))

    ret = []
    for prefix, registered_ats in tmp.items():
        sorted_times = ' '.join(sorted(registered_ats))
        ret.append('{} {}'.format(prefix, sorted_times))

    if not ret:
        ret = ['勤怠記録はありません']

    message.send('{}の勤怠:\n{}'.format(user_name, '\n'.join(ret)))


@respond_to('^勤怠\s+csv$')
@respond_to('^勤怠\s+csv\s+(\d{4}/\d{1,2})$')
def show_kintai_history_csv(message, time=None):
    """指定した月の勤怠記録をCSV形式で返す

    :param message: slackbotの各種パラメータを保持したclass
    :param str time: `/` 区切りの年月(例: 2016/1)
    """
    now = datetime.datetime.now()
    year, month = now.strftime('%Y'), now.strftime('%m')
    if time:
        year, month = time.split('/')
        if month > 12:
            message.send('指定した対象月が12以上の数字です')
            return

    s = Session()
    qs = (s.query(KintaiHistory)
          .filter(func.extract('year', KintaiHistory.registered_at) == year)
          .filter(func.extract('month', KintaiHistory.registered_at) == month)
          .order_by(KintaiHistory.registered_at.asc()))

    tmp = defaultdict(list)
    for q in qs:
        registered_at = q.registered_at.strftime('%Y-%m-%d')
        tmp[registered_at].append((q.is_workon,
                                   '{:%I:%M:%s}'.format(q.registered_at)))

    ret = []
    for day in [i + 1 for i in range(monthrange(int(year), int(month))[1])]:
        aligin_date = '{}-{:02d}-{:02d}'.format(year, int(month), day)
        workon, workoff = '', ''
        for d in sorted(tmp.get(aligin_date, [])):
            if d[0] == 1:
                workon = d[1]
            elif d[0] == 0:
                workoff = d[1]
        ret.append([aligin_date, workon, workoff])

    output = StringIO()
    w = csv.writer(output)
    w.writerows(ret)

    param = {
        'token': settings.API_TOKEN,
        'channels': message.body['channel'],
        'title': '勤怠記録'
    }
    requests.post(settings.FILE_UPLOAD_URL,
                  params=param,
                  files={'file': output.getvalue()})


@respond_to('^勤怠\s+help$')
def show_help_kintai_commands(message):
    """勤怠コマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
