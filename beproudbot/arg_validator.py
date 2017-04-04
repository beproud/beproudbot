from functools import wraps
from inspect import getcallargs
from logging import getLogger

logger = getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, message):
        self.message = message


class BaseArgValidator(object):
    """ArgValidatorの基底クラス。引数のバリデーションを行う。

    使い方

    1. 派生クラスでバリデーション対象の引数名に対応した clean_{xxx} を実装する
    2. バリデーションエラーの場合、 ValidationError 例外を投げる
    3. バリデーションに通過した場合、値を return する

    .skip_args list バリデーションの対象外にする引数名のリスト

    :Example:

    >>> class ArgValidator(BaseArgValidator):
    >>>     skip_args = ['message']
    >>>
    >>>     def clean_b(self, value):
    >>>         if value < 0:
    >>>             raise ValidationError("b must be greater than equal 0")
    >>>
    >>>         return value * 2
    >>>
    >>> @register_arg_validator(ArgValidator)
    >>> def huga(b):
    >>>     print("0 <= {}", b)
    """

    skip_args = []

    def __init__(self, funcname, callargs, extras=[]):
        """__init__

        :param Dict[str, Any] callargs: 引数名と値の辞書
        :param List[str] extras:
            呼び出し時の引数になくてもバリデーションする追加フィールド。
            引数で受け取ったidでdbへ存在チェックし、
            結果を引数で渡すような場面で使う。
        """
        self.callargs = callargs
        self.extras = extras

        self.cleaned_data = {}
        self.errors = {}
        self.funcname = funcname

    def handle_errors(self):
        """バリデーションに失敗した時呼び出されるハンドラ

        オーバーライドして使う
        """
        pass

    def is_valid(self):
        """バリデーションの実行

        :return bool: valid or not
        """
        self.cleaned_data = {}
        self.errors = {}

        for name, given in self.callargs.items():
            # .skip_args の変数は検証しない
            if name in self.skip_args + self.extras:
                self.cleaned_data[name] = given
                continue

            # clean_xxx メソッドがある場合は呼び出して検証
            f = getattr(self, 'clean_{}'.format(name), None)
            if not f or not callable(f):
                self.cleaned_data[name] = given
                logger.debug("do not have clean_%s method", name)
                continue

            try:
                self.cleaned_data[name] = f(given)
            except ValidationError as e:
                self.errors[name] = e.message

        # 追加フィールドの検証
        for extra_name in self.extras:
            f = getattr(self, 'clean_{}'.format(extra_name))
            try:
                self.cleaned_data[extra_name] = f()
            except ValidationError as e:
                self.errors[extra_name] = e.message

        return not self.errors


def register_arg_validator(cls, extras=[]):
    """関数にバリデータを追加する

    .. note::
      - デコレートする関数は可変長の引数をつかえません
      - デコレートする関数への引数の渡し方は現状の実装では
        呼び出し時と一致しません

    :param BaesArgValidator cls: バリデータのクラス
    """
    assert issubclass(cls, BaseArgValidator)

    def _inner(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            callargs = getcallargs(func, *args, **kwargs)

            validator = cls(func.__name__, callargs, extras)

            if not validator.is_valid():
                validator.handle_errors()
                return

            # XXX ここほんとはポジショナル引数でわたせたほうがいいのかな
            return func(**validator.cleaned_data)

        return wrapper

    return _inner
