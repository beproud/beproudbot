import logging
import io
import tempfile
from datetime import datetime
from contextlib import contextmanager

import requests
from PIL import Image
from slackbot.bot import respond_to

from haro.botmessage import botsend

HELP = """
amesh(http://tokyo-ame.jwa.or.jp/)の天気を表示したい
"""

logger = logging.getLogger(__name__)


@contextmanager
def _get_image(url):
    # URLから画像合成準備できたPIL.Imageを返すショートカット関数
    res = requests.get(url)
    b = io.BytesIO(res.content)
    try:
        original_image = Image.open(b)
        converted_image = original_image.convert("RGBA")
        yield converted_image
    finally:
        original_image.close()


@respond_to('^amesh$')
def amesh(message):

    # ameshでは5分ごとにデータが作成されるため、桁を揃えてからリクエストしたい
    # 同じ画像をリクエストすることありそうなのでキャッシュいれたほうがよさそうだけど、
    # 現状不便ないので特に対応をいれていない
    n = datetime.now()
    yyyymmddhh = n.strftime("%Y%m%d%H")
    mm = "{:02d}".format(n.minute // 5 * 5)

    try:
        # 画像の合成
        # 000 はエリアごとの固定値で050,100,150があるけど決め打ちで
        with _get_image("http://tokyo-ame.jwa.or.jp/map/msk000.png") as image_msk, \
            _get_image("http://tokyo-ame.jwa.or.jp/map/map000.jpg") as image_map, \
            _get_image("http://tokyo-ame.jwa.or.jp/mesh/000/{}{}.gif".format(
                yyyymmddhh, mm)) as image_weather:
            merged = Image.alpha_composite(image_map, image_weather)
            merged2 = Image.alpha_composite(merged, image_msk)

        # slack にアップロードするために一時的にtmpfileに書き出す
        with tempfile.NamedTemporaryFile() as tmp:
            name = "{}{}.png".format(yyyymmddhh, mm)
            tmpname = "{}.png".format(tmp.name)
            merged2.save(tmpname)

            # せっかくなので天気もみれるようにしてる
            comment = "時刻: {:%Y年%m月%d日 %H}:{}\n".format(n, mm) + \
                      "公式: http://tokyo-ame.jwa.or.jp/\n" + \
                      "渋谷区の天気: https://weathernews.jp/onebox/35.679311/139.710717/temp=c&q=東京都渋谷区"
            # 外部サイトに投稿してURLを貼る方法(S3とか)だとaccesskey設定等いるのでslackに直接アップロード
            sc = message._client.webapi
            sc.files.upload(
                file_=tmpname,
                initial_comment=comment,
                title=name,
                filename=name,
                channels=message.channel._body["name"],
            )
    except Exception as e:
        botsend(message, "エラーなのでまた叩いてくだし")
        logger.exception("amesh exception")