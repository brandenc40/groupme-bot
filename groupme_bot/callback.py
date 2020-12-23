class Callback:
    __slots__ = ['attachments', 'avatar_url', 'created_at', 'group_id', 'id',
                 'name', 'sender_id', 'sender_type', 'source_guid', 'system',
                 'text', 'user_id']

    def __init__(self, flask_response: dict):
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
