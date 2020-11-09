from unittest.mock import patch

import pytest


class TestGetUserName:
    @pytest.fixture
    def target(self):
        from haro.slack import get_user_name

        return get_user_name

    def test_get_user_name(self, target):
        """ユーザー名が返る事"""
        user_id, name = "U41NH7LFJ", "haro"
        user_info = {user_id: {"name": name, "display_name": "HARO"}}

        with patch("haro.slack.get_users_info", return_value=user_info):
            actual = target(user_id)

        assert name == actual

    def test_get_user_name_with_none(self, target):
        """存在しないユーザー名であればNoneが返る事"""
        user_id = "U41NH7LFJ"

        with patch("haro.slack.get_users_info", return_value={}):
            actual = target(user_id)

        assert None is actual


class TestGetUserDisplayName:
    @pytest.fixture
    def target(self):
        from haro.slack import get_user_display_name

        return get_user_display_name

    def test_get_user_display_name(self, target):
        """表示名が返る事"""
        user_id, display_name = "U41NH7LFJ", "HARO"
        user_info = {user_id: {"name": "haro", "display_name": display_name}}

        with patch("haro.slack.get_users_info", return_value=user_info):
            actual = target(user_id)

        assert display_name == actual

    def test_get_user_display_name_with_empty(self, target):
        """表示名がなければユーザー名が返る事"""
        user_id, name = "U41NH7LFJ", "haro"
        user_info = {user_id: {"name": name, "display_name": ""}}

        with patch("haro.slack.get_users_info", return_value=user_info):
            actual = target(user_id)

        assert name == actual


class TestGetSlackIdByName:
    @pytest.fixture
    def target(self):
        from haro.slack import get_slack_id_by_name

        return get_slack_id_by_name

    def test_get_slack_id_by_name(self, target):
        """ユーザー名からユーザーIDが取得できる事"""
        user_id, name = "U41NH7LFJ", "haro"
        user_info = {user_id: {"name": name, "display_name": ""}}

        with patch("haro.slack.get_users_info", return_value=user_info):
            actual = target(name)

        assert user_id == actual
