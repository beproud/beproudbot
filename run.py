import argparse
from textwrap import dedent
from configparser import ConfigParser, NoSectionError

from slackbot.bot import Bot, default_reply
from db import init_dbsession


def get_argparser():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent('''\
            説明:
            beproudbotの設定ファイルを読み込んだ後にslackbotを起動します'''))

    parser.add_argument('-c', '--config',
                        type=argparse.FileType('r'),
                        required=True,
                        help='ini形式のファイルをファイルパスで指定します')

    return parser


@default_reply
def beproudbot_default_replay(message):
    """コマンドを間違えた時に表示する文字列を返す

    :param message: slackbot.dispatcher.Message
    """
    message.send('コマンドが不明です')


def main():
    """設定ファイルをparseして、slackbotを起動します

    1. configparserで設定ファイルを読み込む
    2. 設定ファイルに `alembic` セクションが設定されているかチェック
    3. 設定ファイルの情報でDB周りの設定を初期化
    4. slackbotの処理を開始
    """

    parser = get_argparser()
    args = parser.parse_args()
    conf = ConfigParser()
    conf.read_file(args.config)

    if not conf.has_section('alembic'):
        raise NoSectionError('alembic')

    init_dbsession(conf['alembic'])
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
