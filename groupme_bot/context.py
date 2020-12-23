class Context:
    __slots__ = ['bot', 'callback']

    def __init__(self, bot, callback):
        """
        Context provided to every handler/scheduled function run by the bot. This provides a clean object containing
        bot the bot in use and the Callback that was sent.

        :param Bot bot:
        :param Callback callback:
        """
        self.bot = bot
        self.callback = callback
