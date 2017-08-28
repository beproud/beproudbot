from unittest.mock import MagicMock, Mock, patch

import pytest

from beproudbot.plugins.redmine import show_ticket_information, USER_NOT_FOUND
from tests.db import session
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
    channel_mock._body = {"id": channel}
    configure = {
        "channel": channel_mock
    }

    message = MagicMock()
    message.configure_mock(**configure)
    message.body = {"user": user_id}
    message.send = Mock()
    return message


@patch('beproudbot.plugins.redmine.get_user_name', lambda x: USER_NAME)
def test_invalid_user(slack_message, session):

    response = show_ticket_information(slack_message, "1234567")
    assert response is None
    assert slack_message.send.called is True
    slack_message.send.assert_called_with(USER_NOT_FOUND.format(USER_NAME))
