import re
import imp

from unittest import mock
import pytest


class TestUpdateKudo:
    @pytest.fixture(scope='class')
    def target_pattern(self):
        with mock.patch('slackbot.bot.listen_to') as mock_listen_to:
            from haro.plugins import thx  # noqa: F401
            imp.reload(thx)  # ensure applying the decorator

        args, _ = mock_listen_to.call_args
        return re.compile(*args)

    @pytest.mark.parametrize(
        'message,expected',
        [
            # スペースなし
            ('name++ reason why you are pleased', True),
            # スペース * 1
            ('name ++ reason why you are pleased', True),
            # スペース * 2
            ('name  ++ reason why you are pleased', True),
            # 全角スペース
            ('name\N{IDEOGRAPHIC SPACE}++ reason why you are pleased', True),
            # @あり
            ('@name++ reason why you are pleased', True),
            # @とスペースあり
            ('@name ++ reason why you are pleased', True),
            # 複数の名前
            ('name1 name2++ reason why you are pleased', True),
            # 複数の名前とスペース
            ('name1 name2 ++ reason why you are pleased', True),
            # NG: プラスとプラスの間にスペース
            ('name+ + reason why you are pleased', False),
            # NG: プラスの後にスペースがない
            ('name++reason why you are pleased', False),
            # NG: プラスが多い
            ('name+++ reason why you are pleased', False),
            # NG: プラスが多い、スペースあり
            ('name +++ reason why you are pleased', False),
            # NG: プラスがすごく多い
            ('name++++ reason why you are pleased', False),
        ]
    )
    def test_pattern(
        self, target_pattern,
        # parameters
        message, expected,
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
        matched = (actual is not None)
        assert matched == expected
