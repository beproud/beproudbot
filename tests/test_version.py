from unittest import mock
import pytest

class TestVersion:
    @pytest.fixture
    def target(self):
        from haro.plugins.version import version
        return version

    @pytest.mark.parametrize(
        'change_log,expected',
        [
            # issue番号が数値
            (
                # ChangeLog.rst
                'Unreleased\n' + \
                '----------\n' + \
                '\n' + \
                'Release Notes - 2020-10-30\n' + \
                '--------------------------\n' + \
                '- [#210] READMEとenv.sampleにREDMINE_API_KEYについて追記\n' + \
                '\n' + \
                'Release Notes - 2020-10-23\n' + \
                '--------------------------\n' + \
                '- [#207] Redmine Reminderが動いていないバグ\n',
                # expected
                'Release Notes - 2020-10-30\n' + \
                '--------------------------\n' + \
                '- [#210] READMEとenv.sampleにREDMINE_API_KEYについて追記\n'
            ),
            # issue番号が数値以外
                (
                # ChangeLog.rst
                'Unreleased\n' + \
                '----------\n' + \
                '\n' + \
                'Release Notes - 2020-10-30\n' + \
                '--------------------------\n' + \
                '- [#foo] READMEとenv.sampleにREDMINE_API_KEYについて追記\n' + \
                '\n' + \
                'Release Notes - 2020-10-23\n' + \
                '--------------------------\n' + \
                '- [#bar] Redmine Reminderが動いていないバグ\n',
                # expected
                'Release Notes - 2020-10-30\n' + \
                '--------------------------\n' + \
                '- [#foo] READMEとenv.sampleにREDMINE_API_KEYについて追記\n'
            )
        ]
    )
    def test_get_version_success(self, target, change_log, expected):
        with mock.patch('haro.plugins.version.read_change_log') as m:
            m.return_value = change_log
            actual = target()
            assert actual == expected

    def test_get_version_failed(self, target):
        with mock.patch('haro.plugins.version.read_change_log') as m:
            # arrange
            m.side_effect = FileNotFoundError
            expected = 'リリースノートが見つかりません'
            # act
            actual = target()
        # assert
        assert actual == expected
