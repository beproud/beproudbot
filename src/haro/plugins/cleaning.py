import datetime
from collections import OrderedDict

from prettytable import PrettyTable
from slackbot.bot import respond_to

from db import Session
from haro.alias import get_slack_id
from haro.botmessage import botsend
from haro.plugins.cleaning_models import Cleaning
from haro.slack import get_user_name

HELP = """
- `$cleaning task`: 掃除作業の一覧を表示する
- `$cleaning list`: 掃除当番の一覧を表示する
- `$cleaning today`: 今日の掃除当番を表示する
- `$cleaning add <user_name> <day_of_week>`: 掃除当番を追加する
- `$cleaning del <user_name> <day_of_week>`: 掃除当番から削除する
- `$cleaning move <user_name> <day_of_week>`: 掃除当番の曜日を移動する
- `$cleaning swap <user_name> <user_name>`: 掃除当番を入れ替える
- `$cleaning help`: cleaningコマンドの使い方を返す
- ※<day_of_week> は月、火、水、木、金が指定可能です
"""

CLEANING_TASKS = [
    'ゴミ集め(各机, シュレッダー) ',
    'ゴミ出し 火曜・金曜',
    '机拭き: bar, showroom, 窓際, おやつ, スタンディング',
    'フリーアドレス席の汚れている机拭き',
    'barのディスプレイから出てるケーブルを後ろ側にある取っ手にかける',
    '空気清浄機のフル稼働(執務室,bar,showroom)',
    '加湿器の注水＆フル稼働(消し忘れ防止のためにタイマーで設定しましょう) 冬場のみ',
]

# 掃除作業を表示用に整形した文字列
FORMATTED_CLEANING_TASKS = ('掃除でやることリスト\n' +
                            '\n'.join(['- [] {}'.format(row) for row in CLEANING_TASKS]))

DAY_OF_WEEK = '月火水木金'


@respond_to('^cleaning\s+help$')
def show_help_cleaning_commands(message):
    """Cleaningコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    botsend(message, HELP)


@respond_to('^cleaning\s+task$')
def show_cleaning_task(message):
    """掃除作業一覧を表示

    :param message: slackbot.dispatcher.Message
    """
    botsend(message, FORMATTED_CLEANING_TASKS)


@respond_to('^cleaning\s+list$')
def show_cleaning_list(message):
    """掃除当番の一覧を表示する

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    dow2users = OrderedDict()
    cleaning = s.query(Cleaning).order_by(Cleaning.day_of_week.asc(), Cleaning.id.asc())
    for c in cleaning:
        user = get_user_name(c.slack_id)
        dow2users.setdefault(c.day_of_week, []).append(user)

    pt = PrettyTable(['曜日', '掃除当番'])
    pt.align['掃除当番'] = 'l'
    for day_of_week, users in dow2users.items():
        dow = DAY_OF_WEEK[day_of_week]
        str_users = ', '.join(users)
        pt.add_row([dow, str_users])
    botsend(message, '```{}```'.format(pt))


@respond_to('^cleaning\s+today$')
def show_today_cleaning_list(message):
    """今日の掃除当番を表示する

    :param message: slackbot.dispatcher.Message
    """
    dow = datetime.datetime.today().weekday()

    s = Session()
    users = [get_user_name(c.slack_id) for
             c in s.query(Cleaning).filter(Cleaning.day_of_week == dow)]
    botsend(message, '今日の掃除当番は{}です'.format('、'.join(users)))


@respond_to('^cleaning\s+add\s+(\S+)\s+(\S+)$')
def cleaning_add(message, user_name, day_of_week):
    """指定した曜日の掃除当番にユーザーを追加する

    :param message: slackbot.dispatcher.Message
    :param str user_name: 掃除当番に登録するユーザー名
    :param str day_of_week: 追加する掃除曜日
    """
    if day_of_week not in DAY_OF_WEEK:
        botsend(message, '曜日には `月` 、 `火` 、 `水` 、 `木` 、 `金` のいずれかを指定してください')
        return

    s = Session()
    slack_id = get_slack_id(s, user_name)
    if not slack_id:
        botsend(message, '{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    q = s.query(Cleaning).filter(Cleaning.slack_id == slack_id)
    if s.query(q.exists()).scalar():
        botsend(message, '{}は既に登録されています'.format(user_name, day_of_week))
        return

    s.add(Cleaning(slack_id=slack_id, day_of_week=DAY_OF_WEEK.index(day_of_week)))
    s.commit()
    botsend(message, '{}を{}曜日の掃除当番に登録しました'.format(user_name, day_of_week))


@respond_to('^cleaning\s+del\s+(\S+)\s+(\S+)$')
def cleaning_del(message, user_name, day_of_week):
    """指定した曜日の掃除当番からユーザーを削除する

    :param message: slackbot.dispatcher.Message
    :param str user_name: 掃除当番から削除するユーザー名
    :param str day_of_week: 削除する掃除当番が登録されている曜日
    """
    if day_of_week not in DAY_OF_WEEK:
        botsend(message, '曜日には `月` 、 `火` 、 `水` 、 `木` 、 `金` のいずれかを指定してください')
        return

    s = Session()
    slack_id = get_slack_id(s, user_name)
    if not slack_id:
        botsend(message, '{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    cleaning_user = (s.query(Cleaning)
                     .filter(Cleaning.slack_id == slack_id)
                     .filter(Cleaning.day_of_week == DAY_OF_WEEK.index(day_of_week))
                     .one_or_none())

    if cleaning_user:
        s.delete(cleaning_user)
        s.commit()
        botsend(message, '{}を{}曜日の掃除当番から削除しました'.format(user_name, day_of_week))
    else:
        botsend(message, '{}は{}曜日の掃除当番に登録されていません'.format(user_name, day_of_week))


@respond_to('^cleaning\s+swap\s+(\S+)\s+(\S+)$')
def cleaning_swap(message, user_name1, user_name2):
    """登録された掃除当番のユーザーの掃除曜日を入れ替える

    :param message: slackbot.dispatcher.Message
    :param str user_name1: 掃除当番の曜日を交換するユーザー名
    :param str user_name2: 掃除当番の曜日を交換するユーザー名
    """

    s = Session()
    slack_id1 = get_slack_id(s, user_name1)
    slack_id2 = get_slack_id(s, user_name2)

    if slack_id1 is None:
        botsend(message, '{}はSlackのユーザーとして存在しません'.format(user_name1))
        return
    if slack_id2 is None:
        botsend(message, '{}はSlackのユーザーとして存在しません'.format(user_name2))
        return
    if slack_id1 == slack_id2:
        botsend(message, '{}と{}は同じSlackのユーザーです'.format(user_name1, user_name2))
        return

    cleaning_user1 = (s.query(Cleaning)
                      .filter(Cleaning.slack_id == slack_id1)
                      .one_or_none())
    cleaning_user2 = (s.query(Cleaning)
                      .filter(Cleaning.slack_id == slack_id2)
                      .one_or_none())

    if not cleaning_user1:
        botsend(message, '{}は掃除当番に登録されていません'.format(user_name1))
        return
    if not cleaning_user2:
        botsend(message, '{}は掃除当番に登録されていません'.format(user_name2))
        return

    cleaning_user1.slack_id = slack_id2
    cleaning_user2.slack_id = slack_id1
    s.commit()
    botsend(message, '{}と{}の掃除当番を交換しました'.format(user_name1, user_name2))


@respond_to('^cleaning\s+move\s+(\S+)\s+(\S+)$')
def cleaning_move(message, user_name, day_of_week):
    """登録された掃除当番のユーザーの掃除曜日を移動させる

    :param message: slackbot.dispatcher.Message
    :param str user_name: 掃除当番の曜日を移動させるユーザー名
    :param str day_of_week: 移動先の曜日名
    """
    if day_of_week not in DAY_OF_WEEK:
        botsend(message, '曜日には `月` 、 `火` 、 `水` 、 `木` 、 `金` のいずれかを指定してください')
        return

    s = Session()
    slack_id = get_slack_id(s, user_name)
    if slack_id is None:
        botsend(message, '{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    cleaning_user = (s.query(Cleaning)
                     .filter(Cleaning.slack_id == slack_id)
                     .one_or_none())

    if not cleaning_user:
        botsend(message, '{}は掃除当番に登録されていません'.format(user_name))
        return

    cleaning_user.day_of_week = DAY_OF_WEEK.index(day_of_week)
    s.commit()
    botsend(message, '{}の掃除当番の曜日を{}曜日に変更しました'.format(user_name, day_of_week))
