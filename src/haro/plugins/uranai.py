import datetime

import requests
from slackbot.bot import respond_to
from haro.botmessage import botsend


def star(n):
    return "★" * n + "☆" * (5 - n)


def uranai(birthday):
    today = datetime.date.today().strftime("%Y/%m/%d")
    r = requests.get("http://api.jugemkey.jp/api/horoscope/free/{}".format(today))
    month, day = int(birthday[:2]), int(birthday[2:])
    period = [20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 23]
    n = (month + 8 + (day >= period[(month - 1) % 12])) % 12
    d = r.json()["horoscope"][today][n]
    for s in ["total", "love", "money", "job"]:
        d[s] = star(d[s])
    return """\
{rank}位 {sign}
総合: {total}
恋愛運: {love}
金運: {money}
仕事運: {job}
ラッキーカラー: {color}
ラッキーアイテム: {item}
{content}""".format(
        **d
    )


@respond_to(r"^uranai\s+(\d{4})$")
def show_uranai_commands(message, birthday):
    """Uranaiコマンドの結果を表示

    :param message: slackbot.dispatcher.Message
    :param birthday: 4桁の誕生日
    """
    botsend(message, uranai(birthday))
