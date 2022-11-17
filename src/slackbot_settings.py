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
REDMINE_API_KEY = os.environ['REDMINE_API_KEY']

##### HARO #####
# デバッグモードにするとログが出るので、開発時には便利
DEBUG = is_true(os.environ['HARO_DEBUG'])
# logging設定は haro.log.setup() で行う

# haroのプロジェクトルート
PROJECT_ROOT = os.environ['PROJECT_ROOT']

##### DB #####
SQLALCHEMY_URL = os.environ['SQLALCHEMY_URL']
SQLALCHEMY_ECHO = os.environ['SQLALCHEMY_ECHO']
SQLALCHEMY_POOL_SIZE = os.environ.get('SQLALCHEMY_POOL_SIZE')

# Waterコマンドメンション先
WATER_EMPTY_TO = os.environ.get('WATER_EMPTY_TO')
WATER_ORDER_NUM = os.environ.get('WATER_ORDER_NUM', 2)
