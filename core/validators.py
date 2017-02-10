import functools
from inspect import getargspec


class Validation:
    """slackbotのバリデーションの実装

    - decoratorをつける関数の第一引数には `slackbot.dispatcher.Message` が指定されている事
    - Validateを継承して作成するclassのinstancemethodとして、validationする引数のvalidate関数を実装する事
    - validate関数名は`validate_{引数名}` とする事
    - 復数のdecoratorを重ねる場合、一番内側に定義する事
    - decoratorの引数には関数のvalidateしたい引数名を文字列で定義する事
    """
    def __init__(self, *args):
        self.args = args

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(message, *args, **kwargs):
            # slackbotの仕様上kwargsが入ってくることはない
            func_argnames = getargspec(func).args[1:]  # 第一引数はskip

            argname2value = {}
            for idx, argname in enumerate(func_argnames):
                argname2value[argname] = value_or_none(args, idx)

            for arg in self.args:
                if arg not in func_argnames:
                    raise KeyError('keyword arguments %s for function %s not found' % (arg, func.__name__))
                if argname2value.get(arg):
                    validate = getattr(self, 'validate_%s' % arg)
                    msg = validate(argname2value[arg])
                    if msg:
                        message.send(msg)
                        return
            return func(message, *args, **kwargs)
        return wrapper


def value_or_none(tpl, idx):
    try:
        return tpl[idx]
    except IndexError:
        return None
