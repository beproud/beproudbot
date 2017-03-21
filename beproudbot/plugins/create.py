import random

from sqlalchemy.orm import join

from slackbot.bot import respond_to
from db import Session
from beproudbot.plugins.create_models import CreatedCommand, Term
from beproudbot.arg_validator import (
    BaseArgValidator,
    ValidationError,
    register_arg_validator,
)


HELP = """
- `$create add hoge`: hogeコマンドを追加する
- `$create del hoge`: hogeコマンドを削除する
- `$create list hoge`: hogeコマンド一覧を表示する

- `$hoge huga`: huga を語録として追加する
- `$hoge del huga`: hugaを語録から削除する
- `$hoge rm huga`: hugaを語録から削除する
- `$hoge pop`: 最後に追加した用語を削除する
- `$hoge list`: 語録の一覧を返す
- `$hoge search <term>`: 語録の一覧からキーワードにマッチするものを返す
- `$create help`: termコマンドの使い方を返す
"""


class TermValidator(BaseArgValidator):
    skip_args = ['message']

    def clean_command(self, command):
        """
        """
        message = self.callargs['message']
        for deco in ['respond_to', 'listen_to']:
            for re_compile in message._plugins.commands.get(deco):
                if re_compile.pattern.split('\s')[0].lstrip('^') == command:
                    raise ValidationError('`{}`は予約語です'.format(command))
        return command

    def clean_term_command(self, command):
        """
        """
        s = Session()
        created_command = (s.query(CreatedCommand)
                            .filter(CreatedCommand.name == command)
                            .one_or_none())
        if not created_command:
            raise ValidationError('`{}`コマンドは登録されていません'.format(command))
        return command

    def clean_has_command(self):
        """
        """
        command = self.callargs['command']
        s = Session()
        created_command = (s.query(CreatedCommand)
                            .filter(CreatedCommand.name == command)
                            .one_or_none())
        if created_command:
            raise ValidationError('`{}`コマンドは既に登録されています'.format(command))

    def handle_errors(self):
        for err_msg in self.errors.values():
            self.callargs['message'].send(err_msg)


@respond_to('^create\s+add\s+(\S+)$')
@register_arg_validator(TermValidator, ['has_command'])
def add_command(message, command):
    """新たにコマンドを作成する

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    s.add(CreatedCommand(name=command, creator=message.body['user']))
    s.commit()
    message.send('`{}`コマンドを登録しました'.format(command))


@respond_to('^create\s+del\s+(\S+)$')
@register_arg_validator(TermValidator)
def del_command(message, term_command):
    """コマンドを削除する

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    created_command = (s.query(CreatedCommand)
                        .filter(CreatedCommand.name == term_command)
                        .one_or_none())
    s.delete(created_command)
    s.commit()
    message.send('`{}`コマンドを削除しました'.format(term_command))


@respond_to('^(\S+)$')
def return_response(message, command):
    """用語コマンドに登録されている応答をランダムに返す

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    created_command = (s.query(CreatedCommand)
                       .filter(CreatedCommand.name == command)
                       .one_or_none())

    if created_command.terms:
        words = [term.word for term in created_command.terms]
        word = random.choice(words)
        message.send(word)
    else:
        message.send('`{}`コマンドにはまだ語録が登録されていません'.format(command))


@respond_to('^(\S+)\s+(.+)')
def response(message, command, params):
    """語録を追加する

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    created_command = (s.query(CreatedCommand)
                        .filter(CreatedCommand.name == command)
                        .one_or_none())
    if not created_command:
        return

    data = params.split(maxsplit=1)
    subcommand = data[0]
    if subcommand == 'pop':
        # 最後に登録された語録を削除
        pop_term(message, created_command)
    elif subcommand == 'list':
        # 語録の一覧を返す
        get_term(message, created_command)
    elif subcommand == 'search':
        # 語録を検索
        search_term(message, created_command, data[1])
    elif subcommand in ('del', 'delete', 'rm', 'remove'):
        # 語録を削除
        del_term(message, created_command, data[1])
    elif subcommand == 'add':
        # 語録を追加
        add_term(message, created_command, data[1])
    else:
        # サブコマンドが存在しない場合も追加
        add_term(message, created_command, params)


def pop_term(message, command):
    """用語コマンドで最後に登録された応答を削除する

    :param message: slackbot.dispatcher.Message
    """
    name = command.name
    # 応答が登録されていない
    if not command.terms:
        msg = 'コマンド `${}` には語録が登録されていません\n'.format(name)
        msg += '`${} add (レスポンス)` で語録を登録してください'.format(name)
        message.send(msg)
        return


def get_term(message, command):
    """用語コマンドに登録されている応答の一覧を返す

    :param message: slackbot.dispatcher.Message
    """
    name = command.name
    if command.terms:
        pretext = 'コマンド `${}` の語録は {} 件あります\n'.format(
            name, len(command.term))
        data = [t.word for t in command.term]
    else:
        msg = 'コマンド `${}` には語録が登録されていません\n'.format(name)
        msg += '`${} add (レスポンス)` で語録を登録してください'.format(name)
        message.send(msg)


def search_term(message, command, keyword):
    """用語コマンドに登録されている応答のうち、キーワードにマッチするものを返す

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    terms = (s.query(Term)
             .filter(Term.created_command == command)
             .filter(Term.word.like('%keyword%')))

    name = command.name
    if terms:
        pretext = 'コマンド `${}` の `{}` を含む応答は {} 件あります\n'.format(
            name, keyword, len(terms))
        data = [t.word for t in terms]
    else:
        message.send('コマンド `${}` に `{}` を含む応答はありません'.format(name, keyword))


def del_term(message, command, word):
    """用語コマンドから応答を削除する

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    term = (s.query(Term)
            .filter(Term.created_command == command.id)
            .filter(Term.word == word)
            .one_or_none())

    name = command.name
    if not term:
        message.send('コマンド `${}` に「{}」は登録されていません'.format(name, word))
        return

    s.delete(term)
    s.commit()

    message.send('コマンド `${}` から「{}」を削除しました'.format(name, word))


def add_term(message, command, word):
    """用語コマンドに応答を追加する

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    term = (s.query(Term)
            .select_from(join(Term, CreatedCommand))
            .filter(CreatedCommand.id == command.id)
            .filter(Term.word == word)
            .one_or_none())

    name = command.name
    if term:
        message.send('コマンド `${}` に「{}」は登録済みです'.format(name, word))
        return
    else:
        message.send('コマンド')

    s.add(Term(created_command=command.id, creator=message.body['user'], word=word))
    s.commit()
    message.send('コマンド `${}` に「{}」を追加しました'.format(name, word))


@respond_to('^create\s+help$')
def show_help_term_commands(message):
    """termコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    message.send(HELP)
