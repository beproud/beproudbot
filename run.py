import argparse
from importlib import import_module

from slackbot.bot import Bot
from db import init_dbsession


def get_argparser():

    parser = argparse.ArgumentParser(
        usage='python run.py [-s | --settings] [settings filename]',
    )

    parser.add_argument('-s', '--settings',
                        nargs='?',
                        type=str,
                        dest='settings_name',
                        help='set `local` or `production`')

    return parser


def main():
    parser = get_argparser()
    args = parser.parse_args()
    if args.settings_name:
        try:
            settings = import_module('settings.%s' % args.settings_name)
            init_dbsession(settings.DATABASE_CONFIG)
            bot = Bot()
            bot.run()
        except ImportError as e:
            print(e)
    else:
        print('--settings options not set')


if __name__ == "__main__":
    main()
