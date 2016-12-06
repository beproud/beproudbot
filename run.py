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
            Description:
            Start slackbot process after loading the beproudbot config file'''))

    parser.add_argument('-c', '--config',
                        type=argparse.FileType('r'),
                        required=True,
                        help='Specify config file')

    return parser


def main():
    """Load parsed config file and start beproudbot

    1. Check existence of config file
    2. Check if the necessary value is set in the config file
    3. Initialize with config value so that DB can be used
    4. Start slackbot process
    """

    parser = get_argparser()
    args = parser.parse_args()
    conf = ConfigParser()

    try:
        conf.read_file(args.config)
    except Error as e:
        sys.exit(e)

    if not conf.has_option('alembic', 'sqlalchemy.url'):
        sys.exit('alembic section or sqlalchemy.url'
                 ' option is not set in the config file')

    init_dbsession(conf['alembic'])
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
