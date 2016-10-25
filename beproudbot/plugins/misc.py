import random
from slackbot.bot import respond_to


@respond_to('^shuffle\s+(.*)')
def shuffle(message, words):
    """指定したキーワードをシャッフルして返す
    """
    words = words.split()
    if len(words) == 1:
        message.send('キーワードを複数指定してください\n`$shuffle word1 word2...`')
    else:
        random.shuffle(words)
        message.send(' '.join(words))


@respond_to('^choice\s+(.*)')
def choice(message, words):
    """指定したキーワードから一つを選んで返す
    """
    words = words.split()
    if len(words) == 1:
        message.send('キーワードを複数指定してください\n`$choice word1 word2...`')
    else:
        message.send(random.choice(words))
