def botsend(message, text):
    """
    スレッドの親かどうかで応答先を切り替える message.send() の代わりの関数

    :param messsage: slackbotのmessageオブジェクト
    :param text: 送信するテキストメッセージ
    """
    message.send(text, thread_ts=(
        message.thread_ts if 'thread_ts' in message.body else None
    ))


def botreply(message, text):
    """
    スレッドの親かどうかで応答先を切り替える message.reply() の代わりの関数

    :param messsage: slackbotのmessageオブジェクト
    :param text: 送信するテキストメッセージ
    """
    message.reply(text, in_thread=('thread_ts' in message.body))
