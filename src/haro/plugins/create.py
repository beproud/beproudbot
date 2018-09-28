import random

from slackbot.bot import respond_to
from sqlalchemy.orm import join

from db import Session
from haro.arg_validator import (
    BaseArgValidator,
    ValidationError,
    register_arg_validator,
)
from haro.botmessage import botsend, webapisend
from haro.plugins.create_models import CreateCommand, Term

HELP = """
- `$create add <command>`: コマンドを追加する
- `$create del <command>`: コマンドを削除する
- `$<command>`: コマンドに登録した語録の中からランダムに一つ返す
- `$<command> <語録>`: 語録を登録する
- `$<command> del <語録>`: 語録を削除する
- `$<command> pop`: 最後に自分が登録した語録を削除する
- `$<command> list`: 登録された語録の一覧を返す
- `$<command> search <keyword>`: 語録の一覧からキーワードを含むものを返す
- `$create help`: createコマンドの使い方を返す
"""


def command_patterns(message):
    """slackbotに実装したコマンドかどうか返す

    :param message: slackbot.dispatcher.Message
    :param str command_name: 確認するコマンド名
    :return list: 実装コマンドの一覧
    """
    commands = set()
    for deco in ['respond_to', 'listen_to']:
        for re_compile in message._plugins.commands.get(deco):
            commands.add(re_compile.pattern.split('\s')[0].lstrip('^').rstrip('$'))
    return commands


class BaseCommandValidator(BaseArgValidator):
    """createコマンドのバリデータの共通クラス
    """
    skip_args = ['message', 'params']

    def has_command(self, command_name):
        """コマンド名が登録済みか返す
        """
        s = Session()
        qs = (s.query(CreateCommand)
              .filter(CreateCommand.name == command_name))
        return s.query(qs.exists()).scalar()

    def get_command(self, command_name):
        """コマンド名が一致するCommandModelを返す
        """
        s = Session()
        command = (s.query(CreateCommand)
                   .filter(CreateCommand.name == command_name)
                   .one_or_none())
        return command

    def handle_errors(self):
        for err_msg in self.errors.values():
            self.callargs['message'].send(err_msg)


class AddCommandValidator(BaseCommandValidator):

    def clean_command_name(self, command_name):
        """コマンド名に対してValidationを適用する
        """
        if self.has_command(command_name):
            raise ValidationError('`${}`コマンドは既に登録されています'.format(command_name))

        if command_name in command_patterns(self.callargs['message']):
            raise ValidationError('`${}`は予約語です'.format(command_name))

        return command_name


class DelCommandValidator(BaseCommandValidator):

    def clean_command_name(self, command_name):
        """コマンド名に対してValidationを適用する
        """
        if not self.has_command(command_name):
            raise ValidationError('`${}`コマンドは登録されていません'.format(command_name))

        if command_name in command_patterns(self.callargs['message']):
            raise ValidationError('`${}`は予約語です'.format(command_name))

        return command_name

    def clean_command(self):
        """valid済のcommand名が存在すればCommandModelを返す
        """
        command_name = self.cleaned_data.get('command_name')
        return self.get_command(command_name)


class RunCommandValidator(BaseCommandValidator):

    def clean_command_name(self, command_name):
        """コマンド名に対してValidationを適用する
        """
        if command_name not in command_patterns(self.callargs['message']):
            if not self.has_command(command_name):
                raise ValidationError('`${}`コマンドは登録されていません'.format(command_name))

        return command_name

    def clean_command(self):
        """valid済のcommand名が存在すればCommandModelを返す
        """
        command_name = self.cleaned_data.get('command_name')
        return self.get_command(command_name)


class ReturnTermCommandValidator(BaseCommandValidator):
    EXCEPT_1WORD_COMMANDS = ['random', 'lunch', 'amesh']

    def clean_command_name(self, command_name):

        """コマンド名に対してValidationを適用する
        """

        # 一文字コマンドをチェックから除外する
        # haroに登録されているコマンドを自動的に除外できるとよさそう
        if command_name in self.EXCEPT_1WORD_COMMANDS:
            return

        if command_name not in command_patterns(self.callargs['message']):
            if not self.has_command(command_name):
                raise ValidationError('`${}`コマンドは登録されていません'.format(command_name))

        if command_name in command_patterns(self.callargs['message']):
            raise ValidationError('`${}`は予約語です'.format(command_name))

        return command_name

    def clean_command(self):
        """valid済のcommand名が存在すればCommandModelを返す
        """
        command_name = self.cleaned_data.get('command_name')
        return self.get_command(command_name)


@respond_to('^create\s+add\s+(\S+)$')
@register_arg_validator(AddCommandValidator)
def add_command(message, command_name):
    """新たにコマンドを作成する

    :param message: slackbot.dispatcher.Message
    :param str command: 登録するコマンド名
    """
    s = Session()

    s.add(CreateCommand(name=command_name, creator=message.body['user']))
    s.commit()
    botsend(message, '`${}`コマンドを登録しました'.format(command_name))


@respond_to('^create\s+del\s+(\S+)$')
@register_arg_validator(DelCommandValidator, ['command'])
def del_command(message, command_name, command=None):
    """コマンドを削除する

    :param message: slackbot.dispatcher.Message
    :param str create_command: 削除するコマンド名
    """
    s = Session()
    s.query(CreateCommand).filter(CreateCommand.id == command.id).delete()
    s.commit()
    botsend(message, '`${}`コマンドを削除しました'.format(command_name))


@respond_to('^(\S+)$')
@register_arg_validator(ReturnTermCommandValidator, ['command'])
def return_term(message, command_name, command=None):
    """コマンドに登録されている語録をランダムに返す

    :param message: slackbot.dispatcher.Message
    :param str command: 語録が登録されているコマンド名
    """
    if command_name:
        if command.terms:
            words = [term.word for term in command.terms]
            word = random.choice(words)
            # #116 URLが展開されて欲しいのでpostMessageで返す
            webapisend(message, word)
        else:
            botsend(message, '`${}`コマンドにはまだ語録が登録されていません'.format(command_name))


@respond_to('^(\S+)\s+(.+)')
@register_arg_validator(RunCommandValidator, ['command'])
def run_command(message, command_name, params, command=None):
    """登録したコマンドに対して各種操作を行う

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    :param str params: 操作内容 + 語録
    """
    # コマンドが登録済みの場合、登録済みコマンドの方で
    # 応答をハンドルしている為ここではリターンする
    if command_name in command_patterns(message):
        return

    data = params.split(maxsplit=1)
    subcommand = data[0]

    try:
        if subcommand == 'pop':
            # 最後に登録された語録を削除
            pop_term(message, command)
        elif subcommand == 'list':
            # 語録の一覧を返す
            get_term(message, command)
        elif subcommand == 'search':
            # 語録を検索
            search_term(message, command, data[1])
        elif subcommand in ('del', 'delete', 'rm', 'remove'):
            # 語録を削除
            del_term(message, command, data[1])
        elif subcommand == 'add':
            # 語録を追加
            add_term(message, command, data[1])
        else:
            # サブコマンドが存在しない場合も追加
            add_term(message, command, params)
    except IndexError:
        # ヘルプを返す
        botsend(message, HELP)


def pop_term(message, command):
    """用語コマンドで最後に登録された応答を削除する

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    """
    s = Session()
    term = (s.query(Term)
            .filter(Term.create_command == command.id)
            .filter(Term.creator == message.body['user'])
            .order_by('-id')
            .first())

    name = command.name
    if term:
        s.delete(term)
        s.commit()
        botsend(message, 'コマンド `${}` から「{}」を削除しました'.format(name, term.word))
    else:
        msg = ('コマンド `${0}` にあなたは語録を登録していません\n'
               '`${0} add (語録)` で語録を登録してください'.format(name))
        botsend(message, msg)


def get_term(message, command):
    """コマンドに登録されている語録の一覧を返す

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    """
    name = command.name
    if command.terms:
        msg = ['コマンド `${}` の語録は {} 件あります'.format(
            name, len(command.terms))]
        for t in command.terms:
            msg.append(t.word)
        botsend(message, '\n'.join(msg))
    else:
        msg = ('コマンド `${0}` には語録が登録されていません\n'
               '`${0} add (語録)` で語録を登録してください'.format(name))
        botsend(message, msg)


def search_term(message, command, keyword):
    """コマンドに登録されている語録のうち、キーワードを含むものを返す

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    :param str keyword: 登録済み語録から検索するキーワード
    """
    s = Session()
    terms = (s.query(Term)
             .filter(Term.create_command == command.id)
             .filter(Term.word.like('%' + keyword + '%')))

    name = command.name
    if terms.count() > 0:
        msg = ['コマンド `${}` の `{}` を含む語録は {} 件あります'.format(
            name, keyword, terms.count())]
        for t in terms:
            msg.append(t.word)
        botsend(message, '\n'.join(msg))
    else:
        botsend(message, 'コマンド `${}` に `{}` を含む語録はありません'.format(
            name, keyword))


def del_term(message, command, word):
    """コマンドから語録を削除する

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    :param str word: 削除する語録
    """
    s = Session()
    term = (s.query(Term)
            .filter(Term.create_command == command.id)
            .filter(Term.word == word)
            .one_or_none())

    name = command.name
    if term:
        s.delete(term)
        s.commit()
        botsend(message, 'コマンド `${}` から「{}」を削除しました'.format(name, word))
    else:
        botsend(message, 'コマンド `${}` に「{}」は登録されていません'.format(name, word))


def add_term(message, command, word):
    """コマンドに語録を追加する

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    :param str word: 登録する語録
    """
    s = Session()
    term = (s.query(Term)
            .select_from(join(Term, CreateCommand))
            .filter(CreateCommand.id == command.id)
            .filter(Term.word == word)
            .one_or_none())

    name = command.name
    if term:
        botsend(message, 'コマンド `${}` に「{}」は登録済みです'.format(name, word))
    else:
        s.add(Term(create_command=command.id, creator=message.body['user'], word=word))
        s.commit()
        botsend(message, 'コマンド `${}` に「{}」を追加しました'.format(name, word))


@respond_to('^create\s+help$')
def show_help_create_commands(message):
    """createコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    botsend(message, HELP)
