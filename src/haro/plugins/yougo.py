import re

import requests
from bs4 import BeautifulSoup
from redminelib import Redmine
from slackbot.bot import respond_to

from slackbot_settings import (
    REDMINE_URL,
    REDMINE_USER_NAME,
    REDMINE_PASSWORD,
)
from db import Session
from haro.plugins.yougo_models import Yougo

REDMINE_LOGIN_URL = REDMINE_URL + '/login'
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


def parse_yougo_page(project_identifie, project_id, channel_id):
    """Redmineの用語集一覧ページにアクセスして用語を取得する

    :param str project_identifie:
       Redmineのプロジェクトのidentifie
    :param int channel_id: SlackのチャンネルID
    :return List[dict]: 辞書形式の用語が入ったリスト
    """
    yougo_url = '{}/projects/{}/glossary'.format(REDMINE_URL,
                                                 project_identifie)

    s = requests.Session()
    bs = BeautifulSoup(s.get(REDMINE_LOGIN_URL).text, 'lxml')
    auth_token = bs.find(attrs={'name': 'authenticity_token'}).get('value')

    param = {
        'username': REDMINE_USER_NAME,
        'password': REDMINE_PASSWORD,
        'authenticity_token': auth_token,
        'autologin': '1',
        'utf8': '&#x2713;',
    }
    s.post(REDMINE_LOGIN_URL, data=param)

    # 用語集一覧HTMLをパース
    soup = BeautifulSoup(s.get(yougo_url).text, "lxml")
    data = []
    tables = soup.find_all('table', class_='list glossary')
    table_bodys = [table.find('tbody') for table in tables]
    headers = [
        'word',
        'english_name',
        'data_type',
        'coding_name',
        'description',
    ]
    for body in table_bodys:
        rows = body.find_all('tr', class_=re.compile("term"))
        for row in rows:
            # glossary_idと編集、削除の要素のtdは削除
            cols = [
                x.text.strip() for x in row.find_all('td')
            ][1:-1]
            if len(cols) == len(headers):
                d = dict(zip(headers, cols))
                d['project_id'] = project_id
                d['channel_id'] = channel_id
                data.append(d)
    return data


def check_slack_channel(project_identifie, channel_name):
    """RedmineProjectとSlackChannelのひも付きのチェック

    Redmineのプロジェクトのカスタムフィールド「SlackChannelName」に
    記載されたSlackChannelからのRequestであればTrue
    """
    redmine = Redmine(REDMINE_URL,
                      username=REDMINE_USER_NAME,
                      password=REDMINE_PASSWORD)

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
    2. 紐づくプロジェクトの用語集一覧ページをパースする
    3. パースしたデータで用語集を更新する
    """
    channel = message.channel
    channel_name = channel._body['name']
    channel_id = channel._body['id']
    project_id = check_slack_channel(project_identifie,
                                     channel_name)

    if project_id:
        yougo_data = parse_yougo_page(project_identifie,
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
        message.send('Slackのチャンネルとプロジェクト名が紐付いていません、'
                     'Redmineプロジェクトの設定画面の `Slack Channel`に'
                     'チャンネル名を設定してください')
