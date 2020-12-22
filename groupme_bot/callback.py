class Callback:
    attachments = None
    avatar_url = None
    created_at = None
    group_id = None
    id = None
    name = None
    sender_id = None
    sender_type = None
    source_guid = None
    system = None
    text = None
    user_id = None

    def __init__(self, flask_response):
        for key, value in flask_response.items():
            self.__setattr__(key, value)

    def is_from_user(self) -> bool:
        return self.sender_type == 'user'
