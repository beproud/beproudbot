import os
import argparse
from textwrap import dedent
from configparser import ConfigParser

from slackbot.bot import Bot
from db import init_dbsession


def get_argparser():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=dedent('''\
            Description:
            Start slackbot process after loading the beproudbot config file'''))

    parser.add_argument('-c', '--config',
                        type=str,
                        required=True,
                        dest='config_name',
                        help='set the config filename')

    return parser


def main():
    """Load parsed config file and start beproudbot
    1. Check existence of config file
    2. Check if the necessary value is set in the config file
    3. Initialize with setting value so that DB can be used
    4. Start slackbot process
    """

    parser = get_argparser()
    args = parser.parse_args()
    config_path = os.path.join(os.path.dirname(__file__),
                               'conf/%s.ini' % args.config_name)

    if os.path.isfile(config_path):
        conf = ConfigParser()
        conf.read(config_path)
        if conf.has_option('alembic', 'sqlalchemy.url'):
            init_dbsession(conf._sections['alembic'])
            bot = Bot()
            bot.run()
        else:
            print('alembic section or sqlalchemy.url option is not\
                   set in the config file')
    else:
        print('No such config file :%s.ini' % args.config_name)


if __name__ == "__main__":
    main()
