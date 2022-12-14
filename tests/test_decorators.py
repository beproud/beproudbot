from unittest import mock

import pytest


class TestCallWhenSlsHaroNotInstalled:
    """call_when_sls_haro_not_installed デコレータのテスト"""

    @pytest.fixture
    def target(self):
        from src.haro.decorators import call_when_sls_haro_not_installed

        return call_when_sls_haro_not_installed

    def test_when_sls_haro_not_installed(self, target):
        """新 haro がチャンネルに追加されていないとき"""
        func = mock.Mock()
        wrapped_func = target(func)

        members = mock.Mock()
        members.body = {
            "ok": True,
            "members": [
                "AAAAAAAAA",
                "BBBBBBBBB",
            ],
            "response_metadata": {
                "next_cursor": "",
            },
        }
        message = mock.Mock()
        message.body = {
            "channel": "C1234567890",
            "text": "$random",
        }
        with mock.patch("slacker.Conversations.members", return_value=members):
            wrapped_func(message)

        # メソッドが呼び出されている
        func.assert_called_once_with(message)

    def test_when_sls_haro_installed(self, target):
        """新 haro がチャンネルに追加されているとき"""
        func = mock.Mock()
        wrapped_func = target(func)

        members = mock.Mock()
        members.body = {
            "ok": True,
            "members": [
                "AAAAAAAAA",
                "U033CS84RAR",  # 新 haro のユーザーID
                "BBBBBBBBB",
            ],
            "response_metadata": {
                "next_cursor": "",
            },
        }
        message = mock.Mock()
        message.body = {
            "channel": "C1234567890",
            "text": "$random",
        }
        with mock.patch("slacker.Conversations.members", return_value=members):
            wrapped_func(message)

        # メソッドが呼び出されていない
        func.assert_not_called()

    def test_when_sls_haro_installed_with_cursor(self, target):
        """新 haro のユーザーIDが、ページングによる2回目のリクエストで取得されたとき"""
        func = mock.Mock()
        wrapped_func = target(func)

        members1 = mock.Mock()
        members1.body = {
            "ok": True,
            "members": [
                "AAAAAAAAA",
                "BBBBBBBBB",
            ],
            "response_metadata": {
                "next_cursor": "XXXXXXXXXXXXXXXXXXXX",
            },
        }
        members2 = mock.Mock()
        members2.body = {
            "ok": True,
            "members": [
                "CCCCCCCCC",
                "DDDDDDDDD",
                "U033CS84RAR",  # 新 haro のユーザーID
            ],
            "response_metadata": {
                "next_cursor": "",
            },
        }
        message = mock.Mock()
        message.body = {
            "channel": "C1234567890",
            "text": "$random",
        }
        with mock.patch("slacker.Conversations.members", side_effect=[members1, members2]) as members_mock:
            wrapped_func(message)

            # members のAPIが2回呼ばれている
            assert members_mock.call_count == 2
            assert members_mock.call_args_list[0] == mock.call("C1234567890", None)
            assert members_mock.call_args_list[1] == mock.call("C1234567890", "XXXXXXXXXXXXXXXXXXXX")

        # メソッドが呼び出されていない
        func.assert_not_called()
