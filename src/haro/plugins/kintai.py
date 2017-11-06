import csv
import datetime
from calendar import monthrange
from collections import defaultdict, OrderedDict
from io import StringIO

import requests
from slackbot import settings
from slackbot.bot import respond_to, listen_to
from sqlalchemy import func, Date, cast

from db import Session
from haro.plugins.kintai_models import KintaiHistory
from haro.slack import get_user_name

HELP = """
- `$kintai show`: 自分の勤怠一覧を直近40日分表示する
- `$kintai csv <year>/<month>`: monthに指定した月の勤怠記録をCSV形式で返す(defaultは当年月)
- `おはよう` ・ `お早う` ・ `出社しました`: 出社時刻を記録します
- `帰ります` ・ `かえります` ・ `退社します`: 退社時刻を記録します
- `$kintai help`: 勤怠コマンドの使い方を返す
"""

DAY_OF_WEEK = '月火水木金土日'


@listen_to('おはよう|お早う|出社しました')
def register_workon_time(message):
    """出社時刻を記録して挨拶を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_id = message.body['user']
    register_worktime(user_id)
    message.reply('おはようございます')


@listen_to('帰ります|かえります|退社します')
def register_workoff_time(message):
    """退社時刻を記録して挨拶を返すコマンド

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_id = message.body['user']
    register_worktime(user_id, is_workon=False)
    message.reply('お疲れ様でした')


def register_worktime(user_id, is_workon=True):
    """出社、退社時間をDBに登録する

    :param str user_id: Slackのuser_id
    :param bool is_workon: 出社か退社かのフラグ、defaltは出社
    """
    today = datetime.date.today()
    s = Session()
    # SQLiteを使用している場合、castできないのでMySQLでdebugする事
    record = (s.query(KintaiHistory)
              .filter(cast(KintaiHistory.registered_at, Date) == today)
              .filter(KintaiHistory.user_id == user_id)
              .filter(KintaiHistory.is_workon.is_(is_workon))
              .one_or_none())
    if record:
        record.registered_at = datetime.datetime.now()
    else:
        s.add(KintaiHistory(user_id=user_id, is_workon=is_workon))
    s.commit()


@respond_to('^kintai\s+show$')
def show_kintai_history(message):
    """直近40日分の勤怠記録を表示します

    :param message: slackbotの各種パラメータを保持したclass
    """
    user_id = message.body['user']
    today = datetime.date.today()
    target_day = today - datetime.timedelta(days=40)

    s = Session()
    qs = (s.query(KintaiHistory)
          .filter(KintaiHistory.user_id == user_id)
          .filter(KintaiHistory.registered_at >= target_day)
          .order_by(KintaiHistory.registered_at.asc()))

    kintai = OrderedDict()
    for q in qs:
        day_of_week = DAY_OF_WEEK[q.registered_at.date().weekday()]
        prefix_day = '{:%Y年%m月%d日}({})'.format(q.registered_at, day_of_week)
        registered_at = '{:%I:%M:%S}'.format(q.registered_at)
        kind = '出社' if q.is_workon else '退社'
        kintai.setdefault(prefix_day, []).append('{}  {}'.format(kind,
                                                                 registered_at))

    rows = []
    for prefix, registered_ats in kintai.items():
        sorted_times = ' '.join(sorted(registered_ats))
        rows.append('{} {}'.format(prefix, sorted_times))

    if not rows:
        rows = ['勤怠記録はありません']

    user_name = get_user_name(user_id)
    message.send('{}の勤怠:\n{}'.format(user_name, '\n'.join(rows)))


@respond_to('^kintai\s+csv$')
@respond_to('^kintai\s+csv\s+(\d{4}/\d{1,2})$')
def show_kintai_history_csv(message, time=None):
    """指定した月の勤怠記録をCSV形式で返す

    :param message: slackbotの各種パラメータを保持したclass
    :param str time: `/` 区切りの年月(例: 2016/1)
    """
    user_id = message.body['user']
    if time:
        year_str, month_str = time.split('/')
    else:
        now = datetime.datetime.now()
        year_str, month_str = now.strftime('%Y'), now.strftime('%m')
    year, month = int(year_str), int(month_str)

    if not 1 <= month <= 12:
        message.send('指定した対象月は存在しません')
        return

    s = Session()
    qs = (s.query(KintaiHistory)
          .filter(KintaiHistory.user_id == user_id)
          .filter(func.extract('year', KintaiHistory.registered_at) == year)
          .filter(func.extract('month', KintaiHistory.registered_at) == month))

    kintai = defaultdict(list)
    for q in qs:
        registered_at = q.registered_at.strftime('%Y-%m-%d')
        kintai[registered_at].append((q.is_workon,
                                      '{:%I:%M:%S}'.format(q.registered_at)))

    rows = []
    for day in range(1, monthrange(year, month)[1] + 1):
        aligin_date = '{}-{:02d}-{:02d}'.format(year, month, day)
        workon, workoff = '', ''
        for d in sorted(kintai[aligin_date]):
            if d[0]:
                workon = d[1]
            else:
                workoff = d[1]
        rows.append([aligin_date, workon, workoff])

    output = StringIO()
    w = csv.writer(output)
    w.writerows(rows)

    param = {
        'token': settings.API_TOKEN,
        'channels': message.body['channel'],
        'title': '勤怠記録'
    }
    requests.post(settings.FILE_UPLOAD_URL,
                  params=param,
                  files={'file': output.getvalue()})


@respond_to('^kintai\s+help$')
def show_help_kintai_commands(message):
    """勤怠コマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    message.send(HELP)
