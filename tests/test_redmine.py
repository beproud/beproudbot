from unittest.mock import MagicMock, Mock, patch
from urllib.parse import urljoin

import pytest
import requests_mock

from haro.plugins.redmine import (show_ticket_information, REDMINE_URL,
                                  RESPONSE_ERROR, NO_CHANNEL_PERMISSIONS,
                                  TICKET_INFO)

from tests.factories.redmine import ProjectChannelFactory, RedmineUserFactory
from tests.db import db

USER_NAME = "Emmanuel Goldstein"


@pytest.fixture
def redmine_user(db, user_id="U023BECGF", api_key="d1d567978001e4f884524a8941a9bbe6a8be87ac"):
    with db.transaction() as session:
        user = RedmineUserFactory.create(
            user_id=user_id,
            api_key=api_key
        )
        session.bulk_save_objects([user])
        session.commit()
    return user


@pytest.fixture
def redmine_project(db, project_id=265, channels="C0AGP8QQH,C0AGP8QQZ"):
    with db.transaction() as session:
        project_channel = ProjectChannelFactory.create(
            project_id=project_id,
            channels=channels
        )
        session.bulk_save_objects([project_channel])
        session.commit()
    return project_channel


@pytest.fixture
def slack_message(channel="C0AGP8QQH", user_id="U023BECGF"):
    channel_mock = Mock()
    channel_mock._body = {"id": channel, "name": "test_channel"}
    configure = {
        "channel": channel_mock
    }

    message = MagicMock()
    message.configure_mock(**configure)
    message.body = {"user": user_id}
    message.send = Mock()
    return message


@pytest.fixture
def no_channel_slack_message():
    return slack_message(channel="111111111")


def test_invalid_user_response(db, slack_message):
    with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
        show_ticket_information(slack_message, "1234567")
        assert slack_message.send.called is False


def test_no_ticket_permissions_response(db, slack_message, redmine_user, redmine_project):
    with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
        with requests_mock.mock() as response:
            ticket_id = "1234567"
            url = urljoin(REDMINE_URL, "issues/%s.json?key=%s" % (ticket_id, redmine_user.api_key))
            response.get(url, status_code=403)
            show_ticket_information(slack_message, ticket_id)
            assert slack_message.send.called is True
            slack_message.send.assert_called_with(RESPONSE_ERROR.format(USER_NAME))


def test_no_channel_permissions_response(db, slack_message, redmine_user, redmine_project):
    with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
        with requests_mock.mock() as response:
            ticket_id = "1234567"
            channel_name = slack_message.channel._body['name']

            url = urljoin(REDMINE_URL, "issues/%s.json?key=%s" % (ticket_id, redmine_user.api_key))
            response.get(url, status_code=200, json={"issue": {"project": {"id": 28}}})

            show_ticket_information(slack_message, ticket_id)
            assert slack_message.send.called is True
            slack_message.send.assert_called_with(NO_CHANNEL_PERMISSIONS.format(ticket_id,
                                                                                channel_name))


def test_successful_response(db, slack_message, redmine_user, redmine_project):
    with patch('haro.plugins.redmine.Session', lambda: db.session) as session:

        client, web_api, chat, post_message = Mock(), Mock(), Mock(), Mock()
        chat.post_message = post_message
        web_api.chat = chat
        client.webapi = web_api
        slack_message._client = client

        with requests_mock.mock() as response:
            ticket_id = "1234567"

            url = urljoin(REDMINE_URL, "issues/%s" % ticket_id)
            ticket = {
                "issue":
                    {
                        "id": ticket_id,
                        "project":
                            {
                                "id": redmine_project.project_id
                            },
                        "author": {
                            "name": "author",
                            "id": 1
                            },
                        "subject": "Test Subject",
                        "description": "Description",
                        "assigned_to": {
                            "name": "assigned to",
                            "id": 1
                            },
                        "status": {
                            "name": "status",
                            "id": 1
                            },
                        "priority": {
                            "name": "priority",
                            "id": 1
                            },
                    },
            }
            mock_url = url + ".json?key=%s" % redmine_user.api_key
            response.get(mock_url, status_code=200, json=ticket)

            show_ticket_information(slack_message, ticket_id)

            assert post_message.called is True


def test_no_channels_no_response(db, no_channel_slack_message, redmine_user, redmine_project):
    with patch('haro.plugins.redmine.Session', lambda: db.session) as session:
        with requests_mock.mock() as response:
            ticket_id = "1234567"

            url = urljoin(REDMINE_URL, "issues/%s.json?key=%s" % (ticket_id, redmine_user.api_key))
            response.get(url, status_code=200, json={"issue": {"project": {"id": 28}}})

            show_ticket_information(no_channel_slack_message, ticket_id)
            assert no_channel_slack_message.send.called is False
