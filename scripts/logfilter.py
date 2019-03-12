from datetime import datetime
import fileinput
import os

here = os.path.dirname(__file__)
LOG_DIR = os.path.abspath(os.path.join(here, '..', 'logs'))
LOG_PREFIX = (
    'db',
    'bot'
)


def match_prefix(name):
    for prefix in LOG_PREFIX:
        if name.startswith(prefix):
            return True
    return False


def main():
    for line in fileinput.input():
        today = datetime.now().strftime('%Y%m%d')
        data = line.split(' ')
        if match_prefix(data[0]):
            log_name = '{}_{}.log'.format(data[0].strip(), today)
            log_file = os.path.join(LOG_DIR, log_name)
            row = ' '.join(data[5:])
        else:
            log_name = 'other_{}.log'.format(today)
            log_file = os.path.join(LOG_DIR, log_name)
            row = line

        with open(log_file, 'a') as fp:
            fp.write(row)


if __name__ == '__main__':
    main()
