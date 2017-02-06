import datetime

from prettytable import PrettyTable

from slackbot.bot import respond_to
from utils.slack import get_user_name, get_slack_id_by_name
from db import Session
from beproudbot.plugins.alias_models import UserAliasName
from beproudbot.plugins.cleaning_models import Cleaning


HELP = """
- `$cleaning task`: 掃除作業の一覧を表示する
- `$cleaning list`: 掃除当番の一覧を表示する
- `$cleaning today`: 今日の掃除当番を表示する
- `$cleaning <day_of_week>`: 指定された曜日の掃除当番を表示する
- `$cleaning add <user_name> <day_of_week>`: 掃除当番を追加する
- `$cleaning del <user_name> <day_of_week>`: 掃除当番から削除する
- `$cleaning swap <user_name> <user_name>`: 掃除当番を入れ替える
- `$cleaning move <user_name> <day_of_week>`: 掃除当番の曜日を移動する
- `$cleaning help`: cleaningコマンドの使い方を返す
- ※<day_of_week> は月、火、水、木、金が指定可能です
"""

CLEANING_TASKS = [
    'ゴミ集め(各机, シュレッダー) 火曜・金曜'
    '机拭き: bar, showroom, 窓際, おやつ, スタンディング',
    'フリーアドレス席の汚れている机拭き',
    'barのディスプレイから出てるケーブルを後ろ側にある取っ手にかける',
    '空気清浄機のフル稼働',
    '加湿器の注水＆フル稼働(消し忘れ防止のためにタイマーで設定しましょう) 冬場のみ',
]

DAY_OF_WEEK = '月火水木金土日'


@respond_to('^cleaning\s+help$')
def show_help_cleaning_commands(message):
    """Cleaningコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    message.send(HELP)


@respond_to('^cleaning\s+task$')
def show_cleaning_task(message):
    """Cleaningコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    formatted = '\n'.join(['- [] {}'.format(row) for row in CLEANING_TASKS])
    message.send('掃除でやることリスト\n{}'.format(formatted))


@respond_to('^cleaning\s+list$')
def show_cleaning_duty(message):
    """掃除当番の一覧を表示する

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    dow2users = {}
    for c in s.query(Cleaning).order_by(Cleaning.day_of_week.asc()):
        user = get_user_name(c.slack_id)
        dow2users.setdefault(c.day_of_week, []).append(user)

    pt = PrettyTable(['day of week', 'username'])
    for day_of_week, users in dow2users.items():
        dow = DAY_OF_WEEK[day_of_week]
        str_users = ','.join(users)
        pt.add_row([dow, str_users])
    message.send('```{}```'.format(pt))


@respond_to('^cleaning\s+today$')
def show_today_cleaning_duty(message):
    """今日の掃除当番を表示する

    :param message: slackbot.dispatcher.Message
    """
    dow = datetime.datetime.today().weekday()

    s = Session()
    users = [get_user_name(c.slack_id) for
             c in s.query(Cleaning).filter(Cleaning.day_of_week == dow)]
    message.send('今日の掃除当番は{}です'.format('、'.join(users)))


@respond_to('^cleaning\s+add\s+(\S+)\s+(\S+)$')
def cleaning_add(message, user_name, day_of_week):
    """指定した曜日の掃除当番にユーザーを追加する

    :param message: slackbot.dispatcher.Message
    :param str user_name: 掃除当番に登録するユーザー名
    :param str day_of_week: 追加する掃除曜日
    """
    if day_of_week not in DAY_OF_WEEK:
        message.send('曜日には `月` 、 `火` 、 `水` 、 `木` 、 `金` のいずれかを指定してください')
        return

    slack_id = get_slack_id_by_name(user_name)
    s = Session()
    user_alias_name = UserAliasName.get_or_none_by_alias_name(s, user_name)

    if user_alias_name:
        slack_id = user_alias_name.slack_id
    if not slack_id:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    q = s.query(Cleaning).filter(Cleaning.slack_id == slack_id)
    if s.query(q.exists()).scalar():
        message.send('{}は既に登録されています'.format(user_name, day_of_week))
        return

    s.add(Cleaning(slack_id=slack_id, day_of_week=DAY_OF_WEEK.index(day_of_week)))
    s.commit()
    message.send('{}を{}曜日の掃除当番に登録しました'.format(user_name, day_of_week))


@respond_to('^cleaning\s+del\s+(\S+)\s+(\S+)$')
def cleaning_del(message, user_name, day_of_week):
    """指定した曜日の掃除当番からユーザーを削除する

    :param message: slackbot.dispatcher.Message
    :param str user_name: 掃除当番から削除するユーザー名
    :param str day_of_week: 削除する掃除当番が登録されている曜日
    """
    if day_of_week not in DAY_OF_WEEK:
        message.send('曜日には `月` 、 `火` 、 `水` 、 `木` 、 `金` のいずれかを指定してください')
        return

    slack_id = get_slack_id_by_name(user_name)
    s = Session()
    user_alias_name = UserAliasName.get_or_none_by_alias_name(s, user_name)

    if user_alias_name:
        slack_id = user_alias_name.slack_id
    if not slack_id:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    cleaning_user = (s.query(Cleaning)
                     .filter(Cleaning.slack_id == slack_id)
                     .filter(Cleaning.day_of_week == DAY_OF_WEEK.index(day_of_week))
                     .one_or_none())

    if cleaning_user:
        s.delete(cleaning_user)
        s.commit()
        message.send('{}を{}曜日の掃除当番から削除しました'.format(user_name, day_of_week))
    else:
        message.send('{}は{}曜日の掃除当番に登録されていません'.format(user_name, day_of_week))


@respond_to('^cleaning\s+swap\s+(\S+)\s+(\S+)$')
def cleaning_swap(message, user_name1, user_name2):
    """登録された掃除当番のユーザーの掃除曜日を入れ替える

    :param message: slackbot.dispatcher.Message
    :param str user_name1: 掃除当番の曜日を交換するユーザー名
    :param str user_name2: 掃除当番の曜日を交換するユーザー名
    """
    slack_id1 = get_slack_id_by_name(user_name1)
    slack_id2 = get_slack_id_by_name(user_name2)

    s = Session()
    user_alias_name = (s.query(UserAliasName)
                       .filter(UserAliasName.alias_name.in_([user_name1, user_name2]))
                       .all())

    for alias in user_alias_name:
        if alias.alias_name == user_name1:
            slack_id1 = alias.slack_id
        if alias.alias_name == user_name2:
            slack_id2 = alias.slack_id

    if slack_id1 is None:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name1))
        return
    if slack_id2 is None:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name2))
        return
    if slack_id1 == slack_id2:
        message.send('{}と{}は同じSlackのユーザーです'.format(user_name1, user_name2))
        return

    cleaning_user1 = (s.query(Cleaning)
                      .filter(Cleaning.slack_id == slack_id1)
                      .one_or_none())
    cleaning_user2 = (s.query(Cleaning)
                      .filter(Cleaning.slack_id == slack_id2)
                      .one_or_none())

    if not cleaning_user1:
        message.send('{}は掃除当番に登録されていません'.format(user_name1))
        return
    if not cleaning_user2:
        message.send('{}は掃除当番に登録されていません'.format(user_name2))
        return

    cleaning_user1.slack_id = slack_id2
    cleaning_user2.slack_id = slack_id1
    s.commit()
    message.send('{}と{}の掃除当番を交換しました'.format(user_name1, user_name2))


@respond_to('^cleaning\s+move\s+(\S+)\s+(\S+)$')
def cleaning_move(message, user_name, day_of_week):
    """登録された掃除当番のユーザーの掃除曜日を移動させる

    :param message: slackbot.dispatcher.Message
    :param str user_name: 掃除当番の曜日を移動させるユーザー名
    :param str day_of_week: 移動先の曜日名
    """
    if day_of_week not in DAY_OF_WEEK:
        message.send('曜日には `月` 、 `火` 、 `水` 、 `木` 、 `金` のいずれかを指定してください')
        return

    slack_id = get_slack_id_by_name(user_name)
    s = Session()
    user_alias_name = UserAliasName.get_or_none_by_alias_name(s, user_name)
    if user_alias_name:
        slack_id = user_alias_name.slack_id

    if slack_id is None:
        message.send('{}はSlackのユーザーとして存在しません'.format(user_name))
        return

    cleaning_user = (s.query(Cleaning)
                     .filter(Cleaning.slack_id == slack_id)
                     .one_or_none())

    if not cleaning_user:
        message.send('{}は掃除当番に登録されていません'.format(user_name))
        return

    cleaning_user.day_of_week = DAY_OF_WEEK.index(day_of_week)
    s.commit()
    message.send('{}の掃除当番の曜日を{}曜日に変更しました'.format(user_name, day_of_week))
