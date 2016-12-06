import sys
import argparse
from textwrap import dedent
from configparser import ConfigParser, Error

from slackbot.bot import Bot
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


def main():
    """設定ファイルをparseして、slackbotを起動します

    1. configparserで読み込めるファイルかチェック
    2. 設定ファイルに必須の設定項目が設定されているかチェック
    3. 1. 2.のチェックで問題なければ設定ファイルの情報でDB周りの設定を初期化
    4. slackbotの処理を開始
    """

    parser = get_argparser()
    args = parser.parse_args()
    conf = ConfigParser()

    try:
        conf.read_file(args.config)
    except Error as e:
        sys.exit(e)

    if not conf.has_option('alembic', 'sqlalchemy.url'):
        sys.exit('設定ファイルにalembicセクション及び、'
                 'sqlalchemy.urlオプションの項目が存在していません')

    init_dbsession(conf['alembic'])
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
