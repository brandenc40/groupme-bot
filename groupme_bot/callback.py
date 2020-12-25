from typing import List


class Callback(object):
    __slots__ = '_callback_dict'

    def __init__(self, callback_dict: dict):
        """
        The callback provided by GroupMe. When any message is sent to the group, GroupMe sends a callback to the
        bots endpoint. This object is generated from the callback JSON to allow for easy use by the bot handlers.

        :param dict callback_dict: A dict with the callback json extracted from the flask response.
        """
        self._callback_dict = callback_dict

    @property
    def attachments(self) -> List[dict]:
        out = self._callback_dict.get("attachments")
        return out if out else []

    @property
    def avatar_url(self) -> str:
        return self._callback_dict.get("avatar_url")

    @property
    def created_at(self) -> int:
        return self._callback_dict.get("created_at")

    @property
    def group_id(self) -> str:
        return self._callback_dict.get("group_id")

    @property
    def id(self) -> str:
        return self._callback_dict.get("id")

    @property
    def name(self) -> str:
        return self._callback_dict.get("name")

    @property
    def sender_id(self) -> str:
        return self._callback_dict.get("sender_id")

    @property
    def sender_type(self) -> str:
        return self._callback_dict.get("sender_type")

    @property
    def source_guid(self) -> str:
        return self._callback_dict.get("source_guid")

    @property
    def system(self) -> bool:
        return self._callback_dict.get("system")

    @property
    def text(self) -> str:
        return self._callback_dict.get("text")

    @property
    def user_id(self) -> str:
        return self._callback_dict.get("user_id")
