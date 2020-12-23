class Context:
    def __init__(self, bot, callback):
        """Context provided to all handler functions at time of execution

        :param bot: The Bot being called
        :param callback: The Callback containing the current incoming message details
        """
        self.bot = bot
        self.callback = callback
