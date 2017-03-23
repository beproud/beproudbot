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
- `$create list hoge`: createコマンドで登録したコマンド一覧を表示する
- `$hoge huga`: hugaを語録として追加する
- `$hoge del huga`: hugaを語録から削除する
- `$hoge rm huga`: hugaを語録から削除する
- `$hoge pop`: 最後に追加した語録を削除する
- `$hoge list`: 語録の一覧を返す
- `$hoge search <keyword>`: 語録の一覧からキーワードにマッチするものを返す
- `$create help`: createコマンドの使い方を返す
"""


class TermValidator(BaseArgValidator):
    skip_args = ['message']

    def clean_command(self, command):
        """指定したコマンド名が実装されているコマンド名だった場合Error
        """
        message = self.callargs['message']
        for deco in ['respond_to', 'listen_to']:
            for re_compile in message._plugins.commands.get(deco):
                if re_compile.pattern.split('\s')[0].lstrip('^') == command:
                    raise ValidationError('`{}`は予約語です'.format(command))
        return command

    def clean_term_command(self, command):
        """指定したコマンド名が登録されていなかった場合Error
        """
        s = Session()
        created_command = (s.query(CreatedCommand)
                            .filter(CreatedCommand.name == command)
                            .one_or_none())
        if not created_command:
            raise ValidationError('`{}`コマンドは登録されていません'.format(command))
        return command

    def clean_has_command(self):
        """指定したコマンドが既に登録済みだった場合Error
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
    :param str command: 登録するコマンド名
    """
    s = Session()
    s.add(CreatedCommand(name=command, creator=message.body['user']))
    s.commit()
    message.send('`{}`コマンドを登録しました'.format(command))


@respond_to('^create\s+del\s+(\S+)$')
@register_arg_validator(TermValidator)
def del_command(message, created_command):
    """コマンドを削除する

    :param message: slackbot.dispatcher.Message
    :param str created_command: 削除するコマンド名
    """
    s = Session()
    created_command = (s.query(CreatedCommand)
                        .filter(CreatedCommand.name == created_command)
                        .one_or_none())
    s.delete(created_command)
    s.commit()
    message.send('`{}`コマンドを削除しました'.format(created_command))


@respond_to('^(\S+)$')
def return_term(message, command):
    """コマンドに登録されている語録をランダムに返す

    :param message: slackbot.dispatcher.Message
    :param str command: 語録が登録されているコマンド名
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


@respond_to('^create\s+list$')
def show_create_commands(message):
    """登録したコマンド一覧を表示する

    :param message: slackbot.dispatcher.Message
    """
    s = Session()
    msg = ['登録されているコマンド']
    for command in s.query(CreatedCommand).all():
        msg.append('${}'.format(command.name))

    message.send('\n'.join(msg))


@respond_to('^(\S+)\s+(.+)')
def retrun(message, command, params):
    """登録したコマンドに対して各種操作を行う

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    :param str params: 操作内容 + 語録
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
    :param str command: 登録済のコマンド名
    """
    s = Session()
    term = (s.query(Term)
            .filter(Term.created_command == command.id)
            .order_by('-id')
            .first())

    name = command.name
    if term:
        s.delete(term)
        s.commit()
        message.send('コマンド `${}` から「{}」を削除しました'.format(name, term.word))
    else:
        msg = ('コマンド `${}` には語録が登録されていません\n'
               '`${} add (語録)` で語録を登録してください'.format(name))
        message.send(msg)


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
        message.send('\n'.join(msg))
    else:
        msg = ('コマンド `${}` には語録が登録されていません\n'
               '`${} add (語録)` で語録を登録してください'.format(name))
        message.send(msg)


def search_term(message, command, keyword):
    """コマンドに登録されている語録のうち、キーワードにマッチするものを返す

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    :param str keyword: 登録済み語録から検索するキーワード
    """
    s = Session()
    terms = (s.query(Term)
             .filter(Term.created_command == command.id)
             .filter(Term.word.like('%' + keyword + '%')))

    name = command.name
    if terms.count() > 0:
        msg = ['コマンド `${}` の `{}` を含む語録は {} 件あります'.format(
            name, keyword, terms.count())]
        for t in terms:
            msg.append(t.word)
        message.send('\n'.join(msg))
    else:
        message.send('コマンド `${}` に `{}` を含む語録はありません'.format(
            name, keyword))


def del_term(message, command, word):
    """コマンドから語録を削除する

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    :param str word: 削除する語録
    """
    s = Session()
    term = (s.query(Term)
            .filter(Term.created_command == command.id)
            .filter(Term.word == word)
            .one_or_none())

    name = command.name
    if term:
        s.delete(term)
        s.commit()
        message.send('コマンド `${}` から「{}」を削除しました'.format(name, word))
    else:
        message.send('コマンド `${}` に「{}」は登録されていません'.format(name, word))


def add_term(message, command, word):
    """コマンドに語録を追加する

    :param message: slackbot.dispatcher.Message
    :param str command: 登録済のコマンド名
    :param str word: 登録する語録
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
    else:
        s.add(Term(created_command=command.id, creator=message.body['user'], word=word))
        s.commit()
        message.send('コマンド `${}` に「{}」を追加しました'.format(name, word))


@respond_to('^create\s+help$')
def show_help_create_commands(message):
    """termコマンドのhelpを表示

    :param message: slackbot.dispatcher.Message
    """
    message.send(HELP)
