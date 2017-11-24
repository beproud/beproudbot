import datetime
import json
import urllib
import numpy as np
from slackbot.bot import respond_to


def star(n):
    return '★' * n + '☆' * (5 - n)


def uranai(dt):
    uranai_dd = [18, 48, 79, 109, 140, 172, 203, 234, 265, 296, 326, 355]
    tdy = datetime.date.today().strftime('%Y/%m/%d')
    n = (np.searchsorted(uranai_dd, (datetime.date(2000, int(dt[:2]), int(dt[2:])) -
                                     datetime.date(2000, 1, 1)).days) + 9) % 12
    with urllib.request.urlopen(f'http://api.jugemkey.jp/api/horoscope/free/{tdy}') as fp:
        d = json.loads(fp.read().decode())['horoscope'][tdy][n]
    return f"""\
{d['rank']}位 {d['sign']}
総合: {star(d['total'])}
恋愛運: {star(d['love'])}
金運: {star(d['money'])}
仕事運: {star(d['job'])}
ラッキーカラー: {d['color']}
ラッキーアイテム: {d['item']}
{d['content']}
"""


@respond_to('^uranai\s+(\S{4})$')
def show_uranai_commands(message, dt):
    """Uranaiコマンドの結果を表示

    :param message: slackbot.dispatcher.Message
    :param dt: 4桁の誕生日
    """
    message.send(uranai(dt))
