from .callback import Callback


class Context:
    def __init__(self, bot, callback: Callback):
        """Context provided to all handler functions at time of execution

        :param bot: The bot being called
        :param Callback callback: The Callback object containing data about the current message
        """
        self.bot = bot
        self.callback = callback
