import re
import importlib

from unittest import mock
import pytest


class TestUpdateKudo:
    @pytest.fixture(scope="class")
    def target_pattern(self):
        with mock.patch("slackbot.bot.listen_to") as mock_listen_to:
            from haro.plugins import kudo

            importlib.reload(kudo)  # ensure applying the decorator

        args, _ = mock_listen_to.call_args
        return re.compile(*args)

    @pytest.mark.parametrize(
        "message,expected",
        [
            # スペースなし
            ("name++", True),
            # スペース * 1
            ("name ++", True),
            # スペース * 2
            ("name  ++", True),
            # @あり
            ("@name++", True),
            # @とスペースあり
            ("@name ++", True),
            # 複数の名前
            ("name1 name2++", True),
            # 複数の名前とスペース
            ("name1 name2 ++", True),
            # NG: プラスとプラスの間にスペース
            ("name+ +", False),
            # NG: プラスの後に文字列が続く
            ("name++following-message", False),
            # NG: プラスが多い
            ("name+++", False),
            # NG: プラスが多い、スペースあり
            ("name +++", False),
            # NG: さらにプラスが多い
            ("name++++", False),
        ],
    )
    def test_pattern(
        self,
        target_pattern,
        # parameters
        message,
        expected,
    ):
        """パターンにマッチするメッセージを確認する

        :param message:
            入力値。
            パターンが適用されるメッセージ
        :param expected:
            期待値。
            マッチすることをを期待する場合はTrue、しない場合はFalse
        """
        # act
        actual = target_pattern.match(message)

        # assert
        matched = actual is not None
        assert matched == expected
