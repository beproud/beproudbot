"""
Settings for slackbot
"""
import os

TRUE_VALUES = ('true', 'yes', 1)


def is_true(arg):
    if str(arg).lower() in TRUE_VALUES:
        return True
    return False


##### SLACK #####
# SlackのAPIトークン
# https://my.slack.com/services/new/bot で生成
API_TOKEN = os.environ['SLACK_API_TOKEN']

# 読み込むpluginのリスト
PLUGINS = [
    'haro.plugins',
]

# コマンドの接頭語
ALIASES = '$'
# コマンド失敗時のエラー通知
if os.getenv('SLACK_ERRORS_TO'):
    ERRORS_TO = os.environ['SLACK_ERRORS_TO']

# Slack ファイルアップロードAPI
FILE_UPLOAD_URL = 'https://slack.com/api/files.upload'

# Redmine チケットAPI
REDMINE_URL = os.environ['REDMINE_URL']

##### HARO #####
# デバッグモードにするとログが出るので、開発時には便利
DEBUG = is_true(os.environ['HARO_DEBUG'])
if DEBUG:
    import logging
    logging.basicConfig(level=logging.DEBUG)

##### DB #####
SQLALCHEMY_URL = os.environ['SQLALCHEMY_URL']
SQLALCHEMY_ECHO = os.environ['SQLALCHEMY_ECHO']
SQLALCHEMY_POOL_SIZE = os.environ.get('SQLALCHEMY_POOL_SIZE')
