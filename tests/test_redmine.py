from unittest.mock import MagicMock, Mock, patch

import pytest
import requests_mock

from beproudbot.plugins.redmine import (show_ticket_information, USER_NOT_FOUND, REDMINE_URL,
                                        NO_TICKET_PERMISSIONS, NO_CHANNEL_PERMISSIONS, TICKET_INFO)
from tests.db import DatabaseManager
from tests.factories.redmine import ProjectChannelFactory, RedmineUserFactory

USER_NAME = "Emmanuel Goldstein"


@pytest.fixture
def redmine_user(user_id="U023BECGF", api_key="d1d567978001e4f884524a8941a9bbe6a8be87ac"):
    return RedmineUserFactory.create(
        user_id=user_id,
        api_key=api_key
    )


@pytest.fixture
def redmine_project(project_id=265, channels="C0AGP8QQH,C0AGP8QQZ"):
    return ProjectChannelFactory.create(
        project_id=project_id,
        channels=channels
    )


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


@patch('beproudbot.plugins.redmine.get_user_name', lambda x: USER_NAME)
def test_invalid_user_response(slack_message):
    db = DatabaseManager()
    db.initialize()

    with patch('beproudbot.plugins.redmine.Session', lambda: db.session) as session:
        show_ticket_information(slack_message, "1234567")
        assert slack_message.send.called is True
        slack_message.send.assert_called_with(USER_NOT_FOUND.format(USER_NAME))


@patch('beproudbot.plugins.redmine.get_user_name', lambda x: USER_NAME)
def test_no_ticket_permissions_response(slack_message, redmine_user):
    db = DatabaseManager()
    db.initialize()

    with db.transaction() as session:
        session.bulk_save_objects([redmine_user])
        session.commit()

    with patch('beproudbot.plugins.redmine.Session', lambda: db.session) as session:
        with requests_mock.mock() as response:
            ticket_id = "1234567"
            url = "{}/{}.json".format(REDMINE_URL, ticket_id)
            response.get(url, status_code=403)

            show_ticket_information(slack_message, ticket_id)
            assert slack_message.send.called is True
            slack_message.send.assert_called_with(NO_TICKET_PERMISSIONS.format(USER_NAME))


@patch('beproudbot.plugins.redmine.get_user_name', lambda x: USER_NAME)
def test_no_channel_permissions_response(slack_message, redmine_user, redmine_project):
    db = DatabaseManager()
    db.initialize()

    with db.transaction() as session:
        session.bulk_save_objects([redmine_user, redmine_project])
        session.commit()

    with patch('beproudbot.plugins.redmine.Session', lambda: db.session) as session:
        with requests_mock.mock() as response:
            ticket_id = "1234567"
            channel_name = slack_message.channel._body['name']

            url = "{}/{}.json".format(REDMINE_URL, ticket_id)
            response.get(url, status_code=200, json={"issue": {"project": {"id": 28}}})

            show_ticket_information(slack_message, ticket_id)
            assert slack_message.send.called is True
            slack_message.send.assert_called_with(NO_CHANNEL_PERMISSIONS.format(ticket_id,
                                                                                channel_name))


@patch('beproudbot.plugins.redmine.get_user_name', lambda x: USER_NAME)
def test_successful_response(slack_message, redmine_user, redmine_project):
    db = DatabaseManager()
    db.initialize()

    with db.transaction() as session:
        session.bulk_save_objects([redmine_user, redmine_project])
        session.commit()

    with patch('beproudbot.plugins.redmine.Session', lambda: db.session) as session:
        with requests_mock.mock() as response:
            ticket_id = "1234567"

            url = "{}/{}.json".format(REDMINE_URL, ticket_id)
            ticket = {
                "issue":
                    {
                        "project":
                            {
                                "id": redmine_project.project_id
                            },
                        "subject": "Test Subject",
                    },
            }
            response.get(url, status_code=200, json=ticket)

            show_ticket_information(slack_message, ticket_id)
            assert slack_message.send.called is True
            slack_message.send.assert_called_with(TICKET_INFO.format(ticket["issue"]["subject"],
                                                                     url[:-5]))
