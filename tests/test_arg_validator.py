import pytest

from unittest.mock import MagicMock


class TestBaseArgValidator():
    """BaseArgValidator のテスト

    基底クラスなので基本的になにも起こらない
    """

    def _makeOne(self, *args, **kwargs):
        from beproudbot.arg_validator import BaseArgValidator
        return BaseArgValidator(*args, **kwargs)

    def test_handle_errors(self):
        """よべる"""
        self._makeOne({}).handle_errors()

    def test_is_valid(self):
        """よべる"""
        assert self._makeOne({}).is_valid()

    def test_is_valid_given_extra(self):
        """予期しない extras が与えられた場合にエラーになる"""
        validator = self._makeOne({}, ['extra_arg'])

        with pytest.raises(AttributeError):
            assert not validator.is_valid()


class TestArgValidator():
    """BaseArgvalidator を継承したクラスのテスト"""

    def _makeOne(self, *args, **kwargs):
        from beproudbot.arg_validator import (
            BaseArgValidator,
            ValidationError,
        )

        class ArgValidator(BaseArgValidator):
            def clean_odd(self, value):
                if not value % 2:
                    raise ValidationError("value should be odd")
                return value

            def clean_pow(self):
                return self.cleaned_data['odd'] * self.cleaned_data['odd']

        return ArgValidator(*args, **kwargs)

    def test_clean_called(self):
        """対応するcleanメソッドが呼ばれる"""
        callargs = {'odd': 1}
        validator = self._makeOne(callargs)
        validator.clean_odd = MagicMock()
        validator.is_valid()
        validator.clean_odd.assert_called_with(callargs['odd'])

    @pytest.mark.parametrize('callargs, expected', [
        ({'odd': 1}, True),
        ({'odd': 2}, False),
    ])
    def test_is_valid(self, callargs, expected):
        validator = self._makeOne(callargs)
        assert validator.is_valid() == expected
        if not validator.is_valid():
            assert 'odd' in validator.errors
            assert validator.errors['odd'] == "value should be odd"

    def test_is_valid_with_extra(self):
        validator = self._makeOne({'odd': 3}, extras=['pow'])
        assert validator.is_valid()
        assert 'pow' in validator.cleaned_data
        assert validator.cleaned_data['pow'] == 9


class TestRegisterArgValidator():
    def _callFUT(self, *args, **kwargs):
        from beproudbot.arg_validator import register_arg_validator
        return register_arg_validator(*args, **kwargs)

    def _validator_class(self):
        from beproudbot.arg_validator import (
            BaseArgValidator,
            ValidationError,
        )

        class ArgValidator(BaseArgValidator):
            def clean_odd(self, value):
                if not value % 2:
                    raise ValidationError("value should be odd")
                return value

        return ArgValidator

    def test_ok(self):
        def _f(odd):
            return odd
        f = self._callFUT(self._validator_class())(_f)
        assert f(1) == 1
        assert f(2) is None
