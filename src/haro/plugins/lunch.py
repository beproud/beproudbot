import re
import random
import xml.dom.minidom as md

import requests
import kml2geojson as k2g
from geopy.distance import vincenty
from slackbot.bot import respond_to
from haro.botmessage import botsend

KML_SOURCE = "https://www.google.com/maps/d/u/0/kml?hl=en&mid=1J4U-QXOe1Zi_4Lw5UxaL8AriG6M&lid=zubJL41y6fLI.k8KrINTXzJI4&forcekml=1"  # NOQA
MAPS_URL_BASE = "http://maps.google.com/maps/ms?ie=UTF&msa=0&msid=101243938118389113627.00047d5491d28f02d4f57&z=19&iwloc=A&ll="  # NOQA
BP_COORDINATES = (35.68641, 139.70343)

HELP = """
- `$lunch`: オフィス近辺のお店情報返す
- `$lunch <keyword>`: 指定したキーワードのお店情報を返す
- `$lunch <keyword> <distance>`: 指定したキーワードと検索距離のお店情報を返す
- `$lunch help`: このコマンドの使い方を返す
"""


def parse_kml_to_json(url):
    """
    指定されたURLよりKMLファイルを取得し、'features'以下のpropertiesのjsonデータを返す。

    :param url: KMLファイルのURL
    :return: jsonデータ（店舗情報）
    """
    r = requests.get(url)
    r.raise_for_status()

    kml_str = md.parseString(r.content)
    layers = k2g.build_layers(kml_str)
    places = layers[0]["features"]

    return places


def get_distance_from_office(destination):
    """
    オフィスとと指定のPointの距離をメートル単位で返す。

    :param destination: 目的地
    :return: 距離（メートル単位）
    """
    office_coordinates = BP_COORDINATES
    destination_coordinates = (
        destination["geometry"]["coordinates"][1],
        destination["geometry"]["coordinates"][0],
    )

    distance = vincenty(office_coordinates, destination_coordinates).meters

    return int(distance)


def lunch(keyword, distance=500):  # NOQA: ignore=C901
    """
    BPランチマップより店舗情報を取得し、オフィス近くの候補１件の情報を返す。
    :keywordの指定がある場合は、店舗情報にキーワードを含むお店からランダムに1件の情報を返す。
    候補がない場合、メッセージを返す。

    :param keyword: 検索用のキーワード(ex.: `ラーメン`)
    :param distance: 検索範囲の指定（ex.: 300）、メートル
    :return: 検索結果の文字列
    """
    walking_distance = distance

    try:
        places = parse_kml_to_json(KML_SOURCE)
    except requests.exceptions.HTTPError as e:
        return """ランチの検索をしたが、次の問題が発生してしまいました。ごめんなさい:cry:\n```{}```""".format(e)

    # 検索キーワード指定があれば、該当する店舗だけの候補列を作る
    if keyword:
        filtered_places = []
        for p in places:
            try:
                if keyword in p["properties"]["description"]:
                    filtered_places.append(p)
            except KeyError:
                pass

        if filtered_places:
            places = filtered_places[:]

        else:
            return """[{}]の店舗情報はありませんでした。\n
            """.format(
                keyword
            )

    # placesに候補がある限り繰り返す
    while places:
        place = random.choice(places)
        if get_distance_from_office(place) == 0:
            places.remove(place)
        elif get_distance_from_office(place) > walking_distance:
            places.remove(place)
        else:
            msg = """\n今日のランチはココ！\n>>>*{}*\n{}\n`{}{},{}`\n_オフィスから{}m_
            """.format(
                place["properties"]["name"],
                place["properties"]["description"],
                MAPS_URL_BASE,
                place["geometry"]["coordinates"][1],
                place["geometry"]["coordinates"][0],
                get_distance_from_office(place),
            )
            msg = re.sub(r"<[^<]+?>", "\n", msg)
            return msg

    return "{}m以内の店舗は見つかりませんでした。".format(walking_distance)


@respond_to("^lunch$")
@respond_to(r"^lunch\s+(\S+)$")
@respond_to(r"^lunch\s+(\S+)\s+(\d+)$")
def show_lunch(message, keyword=None, distance=500):
    """Lunchコマンドの結果を表示する

    :param message: slackbot.dispatcher.Message
    :param keyword: 検索キーワード
    :param distance: 検索範囲 (default 500m)
    """
    if keyword == "help":
        return

    distance = int(distance)

    botsend(message, lunch(keyword, distance))


@respond_to(r"^lunch\s+help$")
def show_help_lunch_commands(message):
    """lunchコマンドのhelpを表示

    :param message: slackbotの各種パラメータを保持したclass
    """
    botsend(message, HELP)
