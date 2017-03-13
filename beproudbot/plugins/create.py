from slackbot.bot import respond_to


HELP = """
- `$create hoge`: hogeコマンドを追加
- `$delete hoge`: hogeコマンドを削除
- `$hoge hogehoge`: hogehoge を語録として追加
- `$hoge del hogehoge`: hogehogeを語録から削除
- `$hoge rm hogehoge`: hogehogeを語録から削除
- `$hoge pop`: 最後に追加した用語を削除
- `$hoge list`: 語録の一覧を返す
- `$hoge search <term>`: 語録の一覧からキーワードにマッチするものを返す
- `create help`  createコマンドの使い方を返す
"""


@respond_to()
def create_command(message):
    """新たにコマンドを作成する

    :param message: slackbot.dispatcher.Message
    """
    pass


@respond_to()
def delete_command(message):
    """コマンドを削除する

    :param message: slackbot.dispatcher.Message
    """
    pass


@respond_to()
def add_term(message):
    """語録を追加する

    :param message: slackbot.dispatcher.Message
    """
    pass


@respond_to()
def delete_term(message):
    """語録を削除する

    :param message: slackbot.dispatcher.Message
    """
    pass


@respond_to()
def search_term(message):
    """語録の一覧からキーワードにマッチするものを返す

    :param message: slackbot.dispatcher.Message
    """
    pass


@respond_to()
def show_term_list(message):
    """語録の一覧からキーワードにマッチするものを返す

    :param message: slackbot.dispatcher.Message
    """
    pass


@respond_to('create\s+help$')
def show_help_create_commands(message):
    """createコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    message.send(HELP)
