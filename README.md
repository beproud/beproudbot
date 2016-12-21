# Haro

Haro is [slackbot](https://github.com/lins05/slackbot "lins05/slackbot: A chat bot for Slack (https://slack.com).") based beproud bot system.

## 事前準備

### APIトークンの取得

- https://my.slack.com/services/new/bot にアクセス
- botの名前を適当に指定して「Add bot integration」ボタンをクリックする
- 「Save Integration」ボタンをクリックして保存する
  - API Token(``xoxb-XXXXXXX-XXXXXXX``)をこのあと使用するので、コピーしておく

### Requirements

- Python 3.5.2 or later.

```bash
$ python3 -m venv env
$ git clone git@github.com:beproud/beproudbot.git
$ cd beproudbot
$ source /path/env/bin/activate
(env)$ cp slackbot_settings.py.sample slackbot_settings.py
(env)$ vi slackbot_settings.py # API Token を記入する
(env)$ pip install -r beproudbot/requirements.txt
```

## 起動方法

```bash
$ source /path/env/bin/activate
# configには設定ファイルのファイルパスを指定します
(env)$ python run.py --config conf/local.ini
```

## Command

### misc plugin

- `$shuffle spam ham eggs`: 指定された単語をシャッフルした結果を返す
- `$choice spam ham eggs`: 指定された単語から一つをランダムに選んで返す

### random plugin

- `$random`: チャンネルにいるメンバーからランダムに一人を選ぶ
- `$random active`: チャンネルにいるactiveなメンバーからランダムに一人を選ぶ
- `$random help`: randomコマンドの使い方を返す

### redbull plugin

- `$redbull count`: RedBullの残り本数を表示する
- `$redbull num`: numの数だけRedBullの本数を減らす(負数の場合、増やす)
- `$redbull history`: 自分のRedBullの消費履歴を表示する
- `$redbull clear`: RedBullのDBデータを削除するtoken付きのコマンドを表示する
- `$redbull csv`: RedBullの月単位の消費履歴をCSV形式で表示する
- `$redbull help`: redbullコマンドの使い方を返す

### water plugin

- `$water count`: 現在の残数を返す
- `$water num`: 水を取り替えた時に使用。指定した数だけ残数を減らす(numが負数の場合、増やす)
- `$water hitsory <num>`: 指定した件数分の履歴を返す(default=10)
- `$water help`: このコマンドの使い方を返す
