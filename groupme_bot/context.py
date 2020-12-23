class Context:
    __slots__ = ['bot', 'callback']

    def __init__(self, bot, callback):
        self.bot = bot
        self.callback = callback
