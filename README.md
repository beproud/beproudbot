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

### misc コマンド

- `$shuffle spam ham eggs`: 指定された単語をシャッフルした結果を返す
- `$choice spam ham eggs`: 指定された単語から一つをランダムに選んで返す

### random コマンド

- `$random`: チャンネルにいるメンバーからランダムに一人を選ぶ
- `$random active`: チャンネルにいるactiveなメンバーからランダムに一人を選ぶ
- `$random help`: randomコマンドの使い方を返す

### redbull コマンド

- `$redbull count`: RedBullの残り本数を表示する
- `$redbull num`: numの数だけRedBullの本数を減らす(負数の場合、増やす)
- `$redbull history`: 自分のRedBullの消費履歴を表示する
- `$redbull clear`: RedBullのDBデータを削除するtoken付きのコマンドを表示する
- `$redbull csv`: RedBullの月単位の消費履歴をCSV形式で表示する
- `$redbull help`: redbullコマンドの使い方を返す

### water コマンド

- `$water count`: 現在の残数を返す
- `$water num`: 水を取り替えた時に使用。指定した数だけ残数を減らす(numが負数の場合、増やす)
- `$water hitsory <num>`: 指定した件数分の履歴を返す(default=10)
- `$water help`: このコマンドの使い方を返す

### kintai コマンド

- `$勤怠`: 自分の勤怠一覧を直近40日分表示する
- `$勤怠 csv <year>/<month>`: monthに指定した月の勤怠記録をCSV形式で返す(defaultは当年月)
- `おはよう`・`お早う`・`出社しました`: 出社時刻を記録します
- `帰ります`・`かえります`・`退社します`: 退社時刻を記録します
- `$勤怠 help`: 勤怠コマンドの使い方を返す

### alias コマンド

- `$alias show [user_name]`: Slackのユーザーに紐づいているエイリアス名一覧を表示する
- `$alias add [user_name] <alias_name>`: Slackのユーザーに紐づくエイリアス名を登録する
- `$alias del [user_name] <alias_name>`: Slackのユーザーに紐づくエイリアス名を削除する
- `$alias help`: aliasコマンドの使い方を返す
- ※各コマンドにてuser_name引数を省略した際には投稿者に対しての操作になります


### cleaning コマンド

- `$cleaning task`: 掃除作業の一覧を表示する
- `$cleaning list`: 掃除当番の一覧を表示する
- `$cleaning today`: 今日の掃除当番を表示する
- `$cleaning add <user_name> <day_of_week>`: 掃除当番を追加する
- `$cleaning del <user_name> <day_of_week>`: 掃除当番から削除する
- `$cleaning move <user_name> <day_of_week>`: 掃除当番の曜日を移動する
- `$cleaning swap <user_name> <user_name>`: 掃除当番を入れ替える
- `$cleaning help`: cleaningコマンドの使い方を返す
- ※<day_of_week> は月、火、水、木、金が指定可能です

### kudo コマンド

- `<name>++`: 指定された名称に対して++します
- `$kudo help`: kudoコマンドの使い方を返す

### thx コマンド

- `[user_name]++ [word]`: 指定したSlackのユーザーにGJする
- `$thx from <user_name>`: 誰からGJされたかの一覧を表示する
- `$thx to <user_name>`: 誰にGJしたかの一覧を返す
- `$thx help`: thxコマンドの使い方を返す
- ※各コマンドにてuser_name引数を省略した際には投稿者に対しての操作になります
