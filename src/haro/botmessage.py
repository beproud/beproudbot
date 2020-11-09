def botsend(message, text):
    """
    スレッドの親かどうかで応答先を切り替える message.send() の代わりの関数

    :param message: slackbotのmessageオブジェクト
    :param text: 送信するテキストメッセージ
    """
    if "thread_ts" in message.body:
        # スレッド内のメッセージの場合
        message.send(text, thread_ts=message.thread_ts)
    else:
        # 親メッセージの場合
        message.send(text)


def botreply(message, text):
    """
    スレッドの親かどうかで応答先を切り替える message.reply() の代わりの関数

    :param message: slackbotのmessageオブジェクト
    :param text: 送信するテキストメッセージ
    """
    if "thread_ts" in message.body:
        # スレッド内のメッセージの場合
        message.reply(text=text, in_thread=True)
    else:
        # 親メッセージの場合
        message.reply(text=text)


def webapisend(message, text):
    """
    botsendのwebapi版

    see https://api.slack.com/methods/chat.postMessage
    """
    sc = message._client.webapi
    channel = message.channel
    channel_id = channel._body["id"]
    if "thread_ts" in message.body:
        sc.chat.post_message(
            channel_id,
            text=text,
            as_user=True,
            unfurl_links=True,
            thread_ts=message.thread_ts,
        )
    else:
        sc.chat.post_message(channel_id, text=text, as_user=True, unfurl_links=True)
