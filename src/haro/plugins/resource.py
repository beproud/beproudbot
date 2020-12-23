"""
`$status`: リソース一覧表示
`$status <add> <name>`: リソース追加
`$status <del,delte,rm,remove> <name>`: リソース削除
`$status <name>`: リソースのステータスをデフォルトに戻す
`$status <name> <value>`: リソースのステータス設定
"""
import random

from slackbot.bot import respond_to
from db import Session
from haro.botmessage import botsend
from haro.plugins.resource_models import Resource


HELP = __doc__
COMMANDS = (
    "help",
    "add",
    "del", "delete", "rm", "remove",
)


@respond_to(r'^status\s+help$')
def show_help(message):
    """Statusコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    botsend(message, HELP)


def show_resources(message):
    """一覧表示

    :param message: slackbot.dispatcher.Message
    """
    channel_id = message.body["channel"]

    s = Session()

    resources = s.query(Resource).filter(
        Resource.channel_id == channel_id,
    ).order_by(Resource.id.asc()).all()
    statuses = []
    for resource in resources:
        if resource.status is None:
            status = " "
        else:
            status = resource.status
        statuses.append("* [{}] {}".format(status, resource.name))
    if not statuses:
        example = random.choice(["なにか", "サーバー", "VM", "ひと", "もの", "こと"])
        statuses = ["これから追加しよう: `$status add {}`".format(example)]

    botsend(message, """```{}```""".format("\n".join(statuses)))


respond_to('^status$')(show_resources)


@respond_to(r'^status\s+add\s+(\S+)$')
def add_resource(message, name):
    """リソースの追加

    :param message: slackbot.dispatcher.Message
    """
    channel_id = message.body["channel"]

    s = Session()
    resource = s.query(Resource).filter(
        Resource.channel_id == channel_id,
        Resource.name == name,
    ).one_or_none()
    if not resource:
        s.add(Resource(
            channel_id=channel_id,
            name=name,
            status=None,
        ))
        s.commit()

    show_resources(message)


@respond_to(r'^status\s+(del|delete|rm|remove)\s+(\S+)$')
def remove_resource(message, _, name):
    """リソースの削除

    :param message: slackbot.dispatcher.Message
    :param str name: リソース名
    """
    channel_id = message.body["channel"]

    s = Session()
    resource = s.query(Resource).filter(
        Resource.channel_id == channel_id,
        Resource.name == name,
    ).one_or_none()
    if resource:
        s.delete(resource)
        s.commit()

    show_resources(message)


@respond_to(r'^status\s+(\S+)$')
def unset_resource_status(message, name):
    """リソースの設定を初期値に戻す

    :param message: slackbot.dispatcher.Message
    :param str name: リソース名
    """
    if name in COMMANDS:
        return

    channel_id = message.body["channel"]

    s = Session()
    resource = s.query(Resource).filter(
        Resource.channel_id == channel_id,
        Resource.name == name,
    ).one_or_none()
    if resource:
        resource.status = None
        s.commit()

    show_resources(message)


@respond_to(r'^status\s+(\S+)\s+(\S+)$')
def set_resource_status(message, name, value):
    """リソースの設定

    :param message: slackbot.dispatcher.Message
    :param str name: リソース名
    :param str value: 状態
    """
    if name in COMMANDS:
        return

    channel_id = message.body["channel"]

    s = Session()
    resource = s.query(Resource).filter(
        Resource.channel_id == channel_id,
        Resource.name == name,
    ).one_or_none()
    if resource:
        resource.status = value
        s.commit()

    show_resources(message)
