import re
import imp
from unittest import mock

import pytest


class TestFindThx:
    @pytest.fixture
    def target(self):
        from haro.plugins.thx import find_thx
        return find_thx

    @pytest.mark.parametrize(
        'text,expected',
        [
            # スペースなし
            (
                'slack_id++ reason ...',
                {
                    'reason ...': [('slack_id', 'slack_id')]
                },
            ),
            # スペース * 1
            (
                'slack_id ++ reason ...',
                {
                    'reason ...': [('slack_id', 'slack_id')]
                },
            ),
            # スペース * 2
            (
                'slack_id  ++ reason ...',
                {
                    'reason ...': [('slack_id', 'slack_id')]
                },
            ),
            # @あり
            (
                '<@slack_id>++ reason ...',
                {
                    'reason ...': [('slack_id', '<@slack_id>')]
                },
            ),
            # @とスペースあり
            (
                '<@slack_id> ++ reason ...',
                {
                    'reason ...': [('slack_id', '<@slack_id>')]
                },
            ),
            # 複数の名前
            (
                'slack_id1 slack_id2++ reason ...',
                {
                    'reason ...': [
                        ('slack_id1', 'slack_id1'),
                        ('slack_id2', 'slack_id2'),
                    ]
                },
            ),
            # 複数の名前とスペース
            (
                'slack_id1 slack_id2 ++ reason ...',
                {
                    'reason ...': [
                        ('slack_id1', 'slack_id1'),
                        ('slack_id2', 'slack_id2'),
                    ]
                },
            ),
            # 複数行
            (
                '\n'.join([
                    'slack_id1++ reason1',
                    'slack_id2++ reason2',
                ]),
                {
                    'reason1': [('slack_id1', 'slack_id1')],
                    'reason2': [('slack_id2', 'slack_id2')],
                },
            ),
            # 複数行 (1行目のプラスがない)
            (
                '\n'.join([
                    'TO BE IGNORED',  # 無視される
                    'slack_id++ reason',
                ]),
                {
                    'reason': [('slack_id', 'slack_id')],
                },
            ),
            # 複数行 (2行目のプラスが多い)
            (
                '\n'.join([
                    'slack_id1++ reason1',
                    'slack_id2+++ reason2',  # 無視される
                ]),
                {
                    'reason1': [('slack_id1', 'slack_id1')],
                },
            ),
            # NG: プラスとプラスの間にスペース
            (
                'slack_id+ + reason ...',
                {},
            ),
            # NG: プラスの後にスペースがない
            (
                'slack_id++reason ...',
                {},
            ),
            # NG: プラスが多い
            (
                'slack_id+++ reason ...',
                {},
            ),
            # NG: プラスが多い、スペースあり
            (
                'slack_id +++ reason ...',
                {},
            ),
            # NG: プラスがすごく多い
            (
                'slack_id++++ reason ...',
                {},
            ),
        ]
    )
    def test_find_user_names(self, target, text, expected):
        """テキストから検出されるユーザーを確認する

        :param str text:
            入力値。このテキストからユーザーを探す
        :param Dict[List[Tuple[str, str]]] text:
            期待値。検出されたthx内容とユーザー
        """
        # act
        with mock.patch(
            'haro.plugins.thx.get_user_name',
            lambda x: x,
        ):
            actual, _, _ = target(None, text)

        # assert
        assert actual == expected


class TestUpdateThx:
    @pytest.fixture(scope='class')
    def target_pattern(self):
        with mock.patch('slackbot.bot.listen_to') as mock_listen_to:
            from haro.plugins import thx
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
