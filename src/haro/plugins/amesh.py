import io
import tempfile
from datetime import datetime

import requests
from PIL import Image
from slackbot.bot import respond_to

HELP = """
amesh(http://tokyo-ame.jwa.or.jp/)の天気を表示したい
"""


@respond_to('^amesh$')
def amesh(message):
    AREA = "000"

    n = yyyymmddhh = datetime.now()
    yyyymmddhh = n.strftime("%Y%m%d%H")
    mm = datetime.now().strftime("%M")
    if mm[1] in ["0", "1", "2", "3", "4"]:
        mm = "{}0".format(mm[0])
    else:
        mm = "{}5".format(mm[0])

    res1 = requests.get("http://tokyo-ame.jwa.or.jp/map/msk{}.png".format(AREA))
    res2 = requests.get("http://tokyo-ame.jwa.or.jp/map/map{}.jpg".format(AREA))
    res3 = requests.get("http://tokyo-ame.jwa.or.jp/mesh/{}/{}{}.gif".format(AREA, yyyymmddhh, mm))
    c1 = io.BytesIO(res1.content)
    c2 = io.BytesIO(res2.content)
    c3 = io.BytesIO(res3.content)
    with Image.open(c1) as im1, Image.open(c2) as im2, Image.open(c3) as im3:

        converted1 = im1.convert("RGBA")
        converted2 = im2.convert("RGBA")
        converted3 = im3.convert("RGBA")

        merged = Image.alpha_composite(converted2, converted3)
        merged2 = Image.alpha_composite(merged, converted1)
        name = "{}_{}{}.png".format(AREA, yyyymmddhh, mm)
        with tempfile.NamedTemporaryFile() as tmp:
            tmpname = "{}.png".format(tmp.name)
            merged2.save(tmpname)

            sc = message._client.webapi
            sc.files.upload(
                file_=tmpname,
                initial_comment="{}:{} http://tokyo-ame.jwa.or.jp/\nhttps://weathernews.jp/onebox/35.679311/139.710717/temp=c&q=東京都渋谷区".format(n.strftime("%Y年%m月%m日 %H"), mm),
                title=name,
                filename=name,
                channels=message.channel._body["name"],
            )

