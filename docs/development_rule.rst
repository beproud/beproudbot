================================
Haroアーキテクチャー
================================

.. contents:: 目次
   :local:


開発
-----


ChangeLog.txtについて
~~~~~~~~~~~~~~~~~~~~~~~

- Haroでは変更履歴をブランチ単位でChangeLog.txtに記載しています

以下のテンプレートに従い記載します

::

   Release Notes - {masterブランチにマージ日}
   -------------------------------------------
   - [PR番号] PR内容

- 例

::

   Release Notes - 2016-12-21
   --------------------------
   - [#4] thxコマンドを追加
   - [#5] kudoコマンドを追加



コマンド実装時に行う事
~~~~~~~~~~~~~~~~~~~~~~~~~~


- HELPコマンドの実装
   - 以下のメリットがあるためHaroではHELPコマンドの実装を推奨しています
      - コマンドの使い方を忘れた時にSlackで使い方を確認できる
      - 開発時のコード自体の説明になる

   - 例

   ::

      HELP = """
      - `$redbull count`: RedBullの残り本数を表示する
      - `$redbull num`: numの数だけRedBullの本数を減らす(負数の場合、増やす)
      - `$redbull history`: 自分のRedBullの消費履歴を表示する
      - `$redbull clear`: RedBullのDBデータを削除するtoken付きのコマンドを表示する
      - `$redbull csv`: RedBullの月単位の消費履歴をCSV形式で表示する
      - `$redbull help`: redbullコマンドの使い方を返す
      """

      @respond_to('^redbull\s+help$')
      def show_help_redbull_commands(message):
          """RedBullコマンドのhelpを表示
          """
          message.send(HELP)

- READMEにコマンドの説明を記載
   - README.mdにコマンドの説明を記載してください

   - 例

   ::

      ### random plugin

      `$random`: チャンネルにいるメンバーからランダムに一人を選ぶ
      `$random active`: チャンネルにいるactiveなメンバーからランダムに一人を選ぶ
      `$random help`: randomコマンドの使い方を返す

- GitHubにPushする場合はtoxを実行する事


ライブラリ
~~~~~~~~~~~~

- ライブラリを導入した場合は `beproudbot/requirements.txt` に記載してください

ブランチ運用
~~~~~~~~~~~~~~

- 基本的に `t{issueナンバー}` という命名規則でブランチを作成してください
- 開発が終わったブランチはPullRequestを出してください


実装方針
----------

モジュール設計
~~~~~~~~~~~~~~~~~

- `beproudbot/beproudbot/plugins/` 直下に用途のコマンド郡単位で実装してください
- 処理の内容を `/plugin/hoge機能.py` として実装、Modelが必要な場合は基本的に `/plugin/hoge機能_models.py` という命名規則で実装してください

コーディング規則
-------------------

- Haro内のPythonコードはシングルクォーテーションで統一してください
- Haro内のPythonコードは一行100文字以内に収めてください
- Haro内で共通して仕様する処理は `beproudbot/utils/` 内に切り出してください
- Haro内で共通して仕様する変数は `beproudbot/slackbot_settings.py` 内に定義してください
- モジュールのimport順は上からPythonビルトイン関数、サード・パーティー製ライブラリ、アプリ内モジュールという順でimportしてください
   - 例

   ::

      import datetime

      from sqlalchemy import func
      from slackbot.bot import respond_to, listen_to

      from db import Session
      from utils.slack import get_user_name
      from beproudbot.plugins.kudo_models import KudoHistory


テスト
--------

- unittestの実行はtoxを実行した際に行われます

::

   $ pip install tox
   $ tox

- tox の install はアプリケーションの virtualenv と同じである必要はありません
- `$ tox` は `tox.ini` と同じディレクトリで実行してください


その他
---------

- SlackIDからユーザー名を取得する際は以下の関数を使ってください
   -  `/beproudbot/utils/slack.py` の `get_user_name()` 関数
   - メリット
      - SlackのusersAPIのキャッシュからを呼び出しているのでSlackに問い合わせを行いません

- ユーザー名からSlackIDを取得する場合、以下の関数を使ってください
   - `beproudbot/utils/alias.py` の `get_slack_id()` 関数
   - メリット
      - SlackのusersAPIのキャッシュから呼び出しているのでSlackに問い合わせを行いません
      - 以下の関数を使う事でAlias登録されているユーザー名からもSlackIDを引く事が可能
