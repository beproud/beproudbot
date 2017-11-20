# from unittest.mock import MagicMock, Mock, patch
# from urllib.parse import urljoin
#
# import pytest
# import requests_mock
#
# from haro.plugins.redmine import (show_ticket_information, USER_NOT_FOUND,
#                                   REDMINE_URL,
#                                   RESPONSE_ERROR, NO_CHANNEL_PERMISSIONS,
#                                   TICKET_INFO)
#
# from tests.factories.redmine import ProjectChannelFactory, RedmineUserFactory
# from tests.db import db
#
# USER_NAME = "Emmanuel Goldstein"
#
#
# @pytest.fixture
# def redmine_user(db, user_id="U023BECGF", api_key="d1d567978001e4f884524a8941a9bbe6a8be87ac"):
#     with db.transaction() as session:
#         user = RedmineUserFactory.create(
#             user_id=user_id,
#             api_key=api_key
#         )
#         session.bulk_save_objects([user])
#         session.commit()
#     return user
#
#
# @pytest.fixture
# def redmine_project(db, project_id=265, channels="C0AGP8QQH,C0AGP8QQZ"):
#     with db.transaction() as session:
#         project_channel = ProjectChannelFactory.create(
#             project_id=project_id,
#             channels=channels
#         )
#         session.bulk_save_objects([project_channel])
#         session.commit()
#     return project_channel
#
#
# @pytest.fixture
# def slack_message(channel="C0AGP8QQH", user_id="U023BECGF"):
#     channel_mock = Mock()
#     channel_mock._body = {"id": channel, "name": "test_channel"}
#     configure = {
#         "channel": channel_mock
#     }
#
#     message = MagicMock()
#     message.configure_mock(**configure)
#     message.body = {"user": user_id}
#     message.send = Mock()
#     return message
#
#
# @pytest.fixture
# def no_channel_slack_message():
#     return slack_message(channel="111111111")
#
#
# @patch('haro.plugins.redmine.get_user_name', lambda x: USER_NAME)
# def test_invalid_user_response(db, slack_message):
#     with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
#         show_ticket_information(slack_message, "1234567")
#         assert slack_message.send.called is True
#         slack_message.send.assert_called_with(USER_NOT_FOUND.format(USER_NAME))
#
#
# @patch('haro.plugins.redmine.get_user_name', lambda x: USER_NAME)
# def test_no_ticket_permissions_response(db, slack_message, redmine_user, redmine_project):
#
#     with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
#         with requests_mock.mock() as response:
#             ticket_id = "1234567"
#             url = urljoin(REDMINE_URL, "%s.json" % ticket_id)
#             response.get(url, status_code=403)
#             show_ticket_information(slack_message, ticket_id)
#             assert slack_message.send.called is True
#             slack_message.send.assert_called_with(RESPONSE_ERROR.format(USER_NAME))
#
#
# @patch('haro.plugins.redmine.get_user_name', lambda x: USER_NAME)
# def test_no_channel_permissions_response(db, slack_message, redmine_user, redmine_project):
#
#     with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
#         with requests_mock.mock() as response:
#             ticket_id = "1234567"
#             channel_name = slack_message.channel._body['name']
#
#             url = urljoin(REDMINE_URL, "%s.json" % ticket_id)
#             response.get(url, status_code=200, json={"issue": {"project": {"id": 28}}})
#
#             show_ticket_information(slack_message, ticket_id)
#             assert slack_message.send.called is True
#             slack_message.send.assert_called_with(NO_CHANNEL_PERMISSIONS.format(ticket_id,
#                                                                                 channel_name))
#
#
# @patch('haro.plugins.redmine.get_user_name', lambda x: USER_NAME)
# def test_successful_response(db, slack_message, redmine_user, redmine_project):
#
#     with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
#         with requests_mock.mock() as response:
#             ticket_id = "1234567"
#
#             url = urljoin(REDMINE_URL, "%s.json" % ticket_id)
#             ticket = {
#                 "issue":
#                     {
#                         "project":
#                             {
#                                 "id": redmine_project.project_id
#                             },
#                         "subject": "Test Subject",
#                     },
#             }
#             response.get(url, status_code=200, json=ticket)
#
#             show_ticket_information(slack_message, ticket_id)
#             assert slack_message.send.called is True
#             slack_message.send.assert_called_with(TICKET_INFO.format(ticket["issue"]["subject"],
#                                                                      url[:-5]))
#
#
# @patch('haro.plugins.redmine.get_user_name', lambda x: USER_NAME)
# def test_no_channels_no_response(db, no_channel_slack_message, redmine_user, redmine_project):
#
#     with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
#         with requests_mock.mock() as response:
#             ticket_id = "1234567"
#
#             url = urljoin(REDMINE_URL, "%s.json" % ticket_id)
#             response.get(url, status_code=200, json={"issue": {"project": {"id": 28}}})
#
#             show_ticket_information(no_channel_slack_message, ticket_id)
#             assert no_channel_slack_message.send.called is False
