THX
=============

Slackに登録されているユーザーに++を行うプラグインです

入力
-------------

例:

::

   OK:
      user_name++ hoge
      user_name ++ hoge
      user_name  ++ hoge
      @user_name++ hoge
      user_name user_name ++ hoge

   NG:
      user_name+ + hoge
      user_name+++ hoge
      user_name++hoge
      user_name,user_name ++ hoge


制限


- 複数ユーザーに++する場合は一行に半角空白文字区切りで複数ユーザー名記載してください
- 改行して++の内容を記載した場合、一番最初の++しか反応しません


出力
-------------

以下の三つのパターンのmessageが返ります


1. Slackのユーザーと一致した名前の場合: `{ユーザー名}({++内容}: {トータルのGJ数}GJ)`
2. Slackのユーザーと一致しなかったが、似た名前が存在する場合: `もしかして: {ユーザー名}`
3. Slackのユーザーと一致しなかった場合: `{ユーザー名}はSlackのユーザーとして存在しません`


その他
-----------

- beproudbotからharo移行時に、Slackユーザーとして存在していないユーザーが行った++はbotユーザーが++したとしてカウントされています
