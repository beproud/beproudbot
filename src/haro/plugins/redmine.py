# from urllib.parse import urljoin
#
# import requests
# from slackbot.bot import listen_to, respond_to
# from slackbot_settings import REDMINE_URL
#
# from db import Session
# from haro.slack import get_user_name
# from haro.plugins.redmine_models import RedmineUser, ProjectChannel
#
# USER_NOT_FOUND = '{}はRedmineUserテーブルに登録されていません。'
# TICKET_INFO = '{}\n{}'
# RESPONSE_ERROR = 'Redmineにアクセスできませんでした。'
# NO_CHANNEL_PERMISSIONS = '{}は{}で表示できません。'
#
#
# HELP = """
# 文章の中にチケット番号(tXXXX)が含まれている場合、チケットのタイトル名とチケットのリンクを表示します。
#
# 例:
# ```
# james [9:00 PM]
# t12345はいつできるのかな？
#
# Haro [9:00 PM]
# SlackからRedmineのチケットを見れるようにしよう
# http://localhost:9000/redmine/issues/12345
# ```
#
# - `$redmine help`: redmineのコマンドの使い方を返す
# """
#
#
# @respond_to('^redmine\s+help$')
# def show_help_redmine_commands(message):
#     """Redmineコマンドのhelpを表示
#     """
#     message.send(HELP)
#
#
# @listen_to('[t](\d{2,})')
# def show_ticket_information(message, ticket_id):
#     """Redmineのチケット情報を参照する.
#
#     :param message: slackbotの各種パラメータを保持したclass
#     :param ticket_id: redmineのチケット番号
#     """
#     s = Session()
#
#     channel = message.channel
#     channel_id = channel._body['id']
#     # message.bodyにuserが含まれている場合のみ反応する
#     if not message.body.get('user'):
#         return
#     user_id = message.body['user']
#
#     user = s.query(RedmineUser).filter(RedmineUser.user_id == user_id).one_or_none()
#
#     if not user:
#         user_name = get_user_name(user_id)
#         message.send(USER_NOT_FOUND.format(user_name))
#         return
#
#     channels = s.query(ProjectChannel.id).filter(ProjectChannel.channels.contains(channel_id))
#     if not s.query(channels.exists()).scalar():
#         return
#
#     ticket_url = urljoin(REDMINE_URL, ticket_id)
#     headers = {'X-Redmine-API-Key': user.api_key}
#     res = requests.get('{}.json'.format(ticket_url), headers=headers)
#
#     if res.status_code != 200:
#         message.send(RESPONSE_ERROR)
#         return
#
#     ticket = res.json()
#     proj_id = ticket['issue']['project']['id']
#     proj_room = s.query(ProjectChannel).filter(ProjectChannel.project_id == proj_id).one_or_none()
#
#     if proj_room and channel_id in proj_room.channels.split(','):
#         message.send(TICKET_INFO.format(ticket['issue']['subject'], ticket_url))
#     else:
#         message.send(NO_CHANNEL_PERMISSIONS.format(ticket_id, channel._body['name']))
