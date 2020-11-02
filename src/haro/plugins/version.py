import re

from slackbot import settings
from slackbot.bot import respond_to
from haro.botmessage import botsend

VERSION_PAT = re.compile(r"Release Notes - [\d-]+")
LOG_PAT = re.compile(r"-\s[#[\w\W]+]\s[\w\W]+")
HELP = """
`$version`: デプロイされているChangeLog.rstから最新の更新内容を表示する
"""


def read_change_log():
    change_log_path = "{}/ChangeLog.rst".format(settings.PROJECT_ROOT)
    try:
        with open(change_log_path, "r", encoding="utf-8") as f:
            change_log = f.read()
        return change_log
    except FileNotFoundError:
        raise FileNotFoundError


def version():
    try:
        body = read_change_log()
    except FileNotFoundError:
        message = "リリースノートが見つかりません"
        return message

    release_notes = body.strip().split("\n")
    latest_row = 0
    for idx, line in enumerate(release_notes):
        if VERSION_PAT.match(line):
            latest_row = idx
            break
    version = release_notes[latest_row].strip()
    log = ""
    for line in release_notes[latest_row + 2 :]:
        if LOG_PAT.match(line):
            log += "{}\n".format(line)
        else:
            break
    message = "{}\n".format(version) + "--------------------------\n" + "{}".format(log)
    return message


@respond_to(r"^version$")
def show_version_commands(message):
    botsend(message, version())


@respond_to(r"^version\s+help$")
def show_help_version_commands(message):
    """versionコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    botsend(message, HELP)
