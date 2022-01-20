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
            "channel": "CCCCCCCCCCC",
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
                "U01V2E7MVLG",  # 新 haro のユーザーID
                "BBBBBBBBB",
            ],
            "response_metadata": {
                "next_cursor": "",
            },
        }
        message = mock.Mock()
        message.body = {
            "channel": "CCCCCCCCCCC",
            "text": "$random",
        }
        with mock.patch("slacker.Conversations.members", return_value=members):
            wrapped_func(message)

        # メソッドが呼び出されていない
        func.assert_not_called()
