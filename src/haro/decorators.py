from functools import wraps
import logging

from slackbot import settings
import slacker


logger = logging.getLogger(__name__)


# Serverless 版 haro のユーザーID
SLS_HARO_USER_ID = "U01V2E7MVLG"


def call_when_sls_haro_not_installed(func):
    """
    Serverless を使った新 haro がチャンネルに追加されていないときのみメソッドを実行するデコレータ

    新 haro に移植済なコマンドに付けて、旧 haro と新 haro が一緒に追加されているチャンネルでは、
    新 haro 側のコマンドが優先されるように制御します

    NOTE: デコレータは下から順に呼ばれるので、このデコレータは respond_to, listen_to よりも上に配置すること

    @call_when_sls_haro_not_installed
    @respond_to("〜")
    def method(message):
        pass
    """
    @wraps(func)
    def wrapper(message, *args, **kwargs):
        # チャンネルのメンバー一覧を取得
        # https://api.slack.com/methods/conversations.members
        channel = message.body['channel']
        webapi = slacker.Slacker(settings.API_TOKEN)
        try:
            cinfo = webapi.conversations.members(channel)
            members = cinfo.body['members']
        except slacker.Error:
            logger.exception('An error occurred while fetching members: channel=%s', channel)
            return

        # チャンネルメンバーに新 haro がいたらメソッドを実行せずに終了
        if SLS_HARO_USER_ID in members:
            logger.info("serverless haro is already installed. channel=%s", channel)
            return

        return func(message, *args, **kwargs)

    return wrapper
