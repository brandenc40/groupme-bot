class Callback:
    __slots__ = ['attachments', 'avatar_url', 'created_at', 'group_id', 'id',
                 'name', 'sender_id', 'sender_type', 'source_guid', 'system',
                 'text', 'user_id']

    def __init__(self, flask_response: dict):
        """
        The callback provided by GroupMe. When any message is sent to the group, GroupMe sends a callback to the
        bots endpoint. This object is generated from the callback JSON to allow for easy use by the bot handlers.

        :param dict flask_response: A dict with the callback json extracted from the flask response.
        """
        self.attachments = None
        self.avatar_url = None
        self.created_at = None
        self.group_id = None
        self.id = None
        self.name = None
        self.sender_id = None
        self.sender_type = None
        self.source_guid = None
        self.system = None
        self.text = None
        self.user_id = None
        for key, value in flask_response.items():
            self.__setattr__(key, value)
