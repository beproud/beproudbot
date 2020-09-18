import random

from slackbot.bot import respond_to
from haro.botmessage import botsend


@respond_to(r'^shuffle\s+(.*)')
def shuffle(message, words):
    """指定したキーワードをシャッフルして返す
    """
    words = words.split()
    if len(words) == 1:
        botsend(message, 'キーワードを複数指定してください\n`$shuffle word1 word2...`')
    else:
        random.shuffle(words)
        botsend(message, ' '.join(words))


@respond_to(r'^choice\s+(.*)')
def choice(message, words):
    """指定したキーワードから一つを選んで返す
    """
    words = words.split()
    if len(words) == 1:
        botsend(message, 'キーワードを複数指定してください\n`$choice word1 word2...`')
    else:
        botsend(message, random.choice(words))
