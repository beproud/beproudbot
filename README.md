[![CircleCI](https://circleci.com/gh/beproud/beproudbot.svg?style=svg)](https://circleci.com/gh/beproud/beproudbot)

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
(env)$ cp env.sample .env
(env)$ vi .env # API Token 等を記入する
(env)$ pip install -r src/requirements.txt
```

## 起動方法

```bash
$ source /path/env/bin/activate
# configには環境変数を指定します
(env)$ export $(cat .env |grep -v '#')
(env)$ cd src && python run.py
```

### Docker

```bash
# MySQL を使用する場合先に立ち上げておく
# docker-compose up -d db
# bot の起動
$ docker-compose build bot
$ docker-compose run -d bot
# コンテナにはいる
$ docker-compose run --rm bot bash
# 終了
# docker-compose down
```

## DB操作

alembic を使用します

### マイグレーション

```bash
(env)$ export $(cat .env |grep -v '#')
(env)$ cd src && alembic --config alembic/conf.ini upgrade head
```

### マイグレーションファイル作成

`env.py`の設定を読み込み、`versions`以下にマイグレーションファイルが書き出されます

```bash
(env)$ export $(cat .env |grep -v '#')
(env)$ cd src && alembic --config alembic/conf.ini revision --autogenerate -m "my message"
```

#### Procfile 使用

マイグレーション等の操作は `honcho` を使用して操作することができます。

honchoは .env を自動的に読み込み、スクリプトを開始することができます。

```bash
(env)$ pip install honcho
# honcho start bot
# honcho start migrate
# honcho start makemigrations
```

## 環境構築

ansible の `configure` タグを使用します。

```bash
$ (cd beproudbot/deployment && ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml)
# 環境変数は `ENVIRONMENT_FILE_PATH` を指定することができます
$ (cd beproudbot/deployment && ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml "ENVIRONMENT_FILE_PATH=path/to/.env")
# MySQL をインストールしない場合 `use_local_mysql_server=false` とすることで設定をスキップできます
$ (cd beproudbot/deployment && ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml --tags=configure -e "use_local_mysql_server=$use_local_mysql_server")
```

## デプロイ

ansible の `deploy` タグを使用します

```bash
$ (cd beproudbot/deployment && ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml --tags=deploy)
# `git_version` でブランチ/タグ/リビジョンを指定することができます
$ (cd beproudbot/deployment && ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml --tags=deploy -e "git_version=branch_name")
# VM開発時は `git_sync_local` でローカルファイルを配備することができます
# また `git_force_checkout` で --force checkout できます
$ (cd beproudbot/deployment && ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml --tags=deploy -e "git_sync_local=true" -e "git_force_checkout=true")
```

環境変数からまとめてまとめて引数に渡す場合の例は以下です

```bash
$ (cd beproudbot/deployment && ~/venv_ansible/bin/ansible-playbook -i hosts --connection local site.yml \
  -e "ENVIRONMENT_FILE_PATH=$ENVIRONMENT_FILE_PATH" \
  -e "use_local_mysql_server=$use_local_mysql_server" \
  -e "git_force_checkout=$git_force_checkout" \
  -e "git_sync_local=$git_sync_local" \
  -e "git_version=$git_version")
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

- `$kintai show`: 自分の勤怠一覧を直近40日分表示する
- `$kintai csv <year>/<month>`: monthに指定した月の勤怠記録をCSV形式で返す(defaultは当年月)
- `おはよう`・`お早う`・`出社しました`: 出社時刻を記録します
- `帰ります`・`かえります`・`退社します`: 退社時刻を記録します
- `$kintai help`: 勤怠コマンドの使い方を返す

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

### create コマンド

- `$create add <command>`: コマンドを追加する
- `$create del <command>`: コマンドを削除する
- `$<command>`: コマンドに登録した語録の中からランダムに一つ返す
- `$<command> <語録>`: 語録を登録する
- `$<command> del <語録>`: 語録を削除する
- `$<command> pop`: 最後に自分が登録した語録を削除する
- `$<command> list`: 登録された語録の一覧を返す
- `$<command> search <keyword>`: 語録の一覧からキーワードを含むものを返す
- `$create help`: createコマンドの使い方を返す

### kudo コマンド

- `<name>++`: 指定された名称に対して++します
- `$kudo help`: kudoコマンドの使い方を返す

### thx コマンド

- `[user_name]++ [word]`: 指定したSlackのユーザーにGJする
- `$thx from <user_name>`: 誰からGJされたかの一覧を表示する
- `$thx to <user_name>`: 誰にGJしたかの一覧を返す
- `$thx help`: thxコマンドの使い方を返す
- ※各コマンドにてuser_name引数を省略した際には投稿者に対しての操作になります

### redmine コマンド

- `/msg @haro $redmine key xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`: 自分のRedmineのAPIキーを登録する
- `$redmine add redmine-project-identifier`: コマンドを実行したSlackチャンネルとRedmineのプロジェクトを連携させます
- `$redmine remove redmine-project-identifier`: コマンドを実行したSlackチャンネルとRedmineプロジェクトの連携を解除します

文章の中にチケット番号(tXXXX)が含まれている場合、チケットのタイトル名とチケットのリンクを表示します。

例:
```
james [9:00 PM]
t12345はいつできるのかな？

Haro [9:00 PM]
SlackからRedmineのチケットを見れるようにしよう
http://localhost:9000/redmine/issues/12345
```

- `$redmine help`: redmineのコマンドの使い方を返す
