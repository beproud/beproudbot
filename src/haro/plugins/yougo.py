import csv
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from redminelib import Redmine
from slackbot.bot import respond_to
from contextlib import closing

from slackbot_settings import (
    REDMINE_URL,
    REDMINE_HARO_USERNAME,
    REDMINE_HARO_PASSWORD,
    REDMINE_HARO_APIKEY,
)
from db import Session
from haro.plugins.yougo_models import Yougo

REDMINE_LOGIN_URL = urljoin(REDMINE_URL, 'login')

HELP = """
- `$yougo load <RedmineProject名>`: Redmineプロジェクトに紐づく用語集を更新
- `$yougo search <用語>`: 用語を検索する
- `$ys <用語>`: 用語を検索する(ショートカットコマンド)
- `$yougo help`: yougoコマンドの使い方を返す
"""

YOUGO_TEMPLATE = """\
```
用語: {word}
英語名: {english_name}
データ型: {data_type}
コーディング用名称例: {coding_name}
説明:
{description}
```
"""


@respond_to('^yougo\s+help$')
def show_help_yougo_commands(message):
    """用語コマンドのHELPを表示
    """
    message.send(HELP)


@respond_to('^ys\s+(.*)')
@respond_to('^yougo\s+search\s+(.*)')
def search_yougo(message, word):
    """用語集から用語を検索して結果を表示

    :param str word: 検索する用語
    """
    channel = message.channel
    channel_id = channel._body['id']

    s = Session()
    yougo = (s.query(Yougo)
             .filter(Yougo.word == word)
             .filter(Yougo.channel_id == channel_id)
             .one_or_none())

    if yougo:
        message.send(YOUGO_TEMPLATE.format(**yougo.__dict__))
    else:
        message.send('用語: `{}` は用語集に登録されていません'.format(word))


def load_yougo(project_identifie, project_id, channel_id):
    """Redmineの用語集一覧ページにアクセスして用語を取得する

    :param str project_identifie:
       Redmineのプロジェクトのidentifie
    :param int channel_id: SlackのチャンネルID
    :return List[dict]: 辞書形式の用語が入ったリスト
    """
    yougo_url = '{}/projects/{}/glossary.csv'.format(REDMINE_URL,
                                                     project_identifie)

    s = requests.Session()
    bs = BeautifulSoup(s.get(REDMINE_LOGIN_URL).text, 'lxml')
    auth_token = bs.find(attrs={'name': 'authenticity_token'}).get('value')

    param = {
        'username': REDMINE_HARO_USERNAME,
        'password': REDMINE_HARO_PASSWORD,
        'authenticity_token': auth_token,
        'autologin': '1',
        'utf8': '&#x2713;',
    }
    s.post(REDMINE_LOGIN_URL, data=param)
    data = []
    with closing(s.get(yougo_url, stream=True)) as r:
        r.encoding = r.apparent_encoding
        rows = csv.reader(r.text.splitlines(), delimiter=',')
        for row in rows:
            data.append({
                'word': row[2],
                'english_name': row[3],
                'data_type': row[7],
                'coding_name': row[8],
                'description': row[13],
                'project_id': project_id,
                'channel_id': channel_id,
            })
    return data


def check_slack_channel(project_identifie, channel_name):
    """RedmineProjectとSlackChannelのひも付きのチェック

    Redmineのプロジェクトのカスタムフィールド「SlackChannelName」に
    記載されたSlackChannelからのRequestであればTrue
    """
    redmine = Redmine(REDMINE_URL, key=REDMINE_HARO_APIKEY)

    try:
        project = redmine.project.get(project_identifie)
    except Exception:
        return
    for v in project.custom_fields.values():
        if v.get('name') == 'Slack Channel':
            if channel_name.replace('#', '') == v.get('value'):
                return project.id


@respond_to('^yougo\s+load\s+(\S+)$')
def load_to_db(message, project_identifie):
    """DBの用語集データの更新

    :param str project_identifie:
       Redmineのプロジェクトのidentifie

    1. コマンドがCallされたSlackのチャンネル名が、
       Redmineのプロジェクトと紐付いているかチェック
    2. RedmineにHaroユーザーでログイン
    3. 紐づくプロジェクトの用語集一覧csvをダウンロード
    4. csvのデータで用語集を更新する
    """
    channel = message.channel
    channel_id = channel._body['id']
    channel_name = channel._body.get('name', '')
    project_id = check_slack_channel(project_identifie,
                                     channel_name)

    if project_id:
        yougo_data = load_yougo(project_identifie,
                                project_id,
                                channel_id)
        s = Session()
        # project_idに紐づく用語を全て削除
        s.query(Yougo).filter(Yougo.project_id == project_id).delete()
        s.commit()
        # DBに用語を全て保存
        Yougo.__table__.insert().execute(yougo_data)
        message.send('用語集を取り込みました')
    else:
        # チャンネル名がない場所で実行した場合(個人のチャンネル等)もここで返る
        message.send('Slackのチャンネルとプロジェクト名が紐付いていません、'
                     'Redmineプロジェクトの設定画面の `Slack Channel`に'
                     'チャンネル名を設定してください')
