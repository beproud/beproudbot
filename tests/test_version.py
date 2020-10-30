import pytest
import responses

class TestVersion:
    @pytest.fixture
    def target(self):
        from haro.plugins.version import version
        return version

    @responses.activate
    @pytest.mark.parametrize(
        'change_log,expected',
        [
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
            )
        ]
    )
    def test_get_version(self, target, change_log, expected):
        responses.add(
            responses.GET,
            'https://raw.githubusercontent.com/beproud/beproudbot/master/ChangeLog.rst',
            body=change_log
        )
        actual = target()
        assert actual == expected
