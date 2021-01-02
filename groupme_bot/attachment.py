from typing import List, Union, Dict


class InvalidAttachment(Exception):
    pass


class Attachment(object):
    __slots__ = '_kwargs'
    _list_keys = ('charmap', 'loci', 'user_ids')

    def __init__(self, **kwargs):
        self._kwargs: dict = kwargs

    @property
    def type(self):
        return self._kwargs.get('type')

    def to_dict(self) -> Dict[str, Union[str, List]]:
        """
        Converts the class instance to a dictionary with properly type casted values
        :return: A dict containing the properly type casted values
        """
        out = {}
        for key, value in self._kwargs.items():
            if key in self._list_keys:
                out[key] = value if value else []
            else:
                out[key] = str(value)
        return out


class ImageAttachment(Attachment):
    def __init__(self, image_url: str):
        Attachment.__init__(self, type='image', url=image_url)

    @property
    def url(self):
        return self._kwargs.get('url')


class LocationAttachment(Attachment):
    def __init__(self, name: str, lat: Union[str, float, int], lng: Union[str, float, int]):
        Attachment.__init__(self, type='location', name=name, lat=lat, lng=lng)

    @property
    def name(self):
        return self._kwargs.get('name')

    @property
    def lat(self):
        return self._kwargs.get('lat')

    @property
    def lng(self):
        return self._kwargs.get('lng')


class SplitAttachment(Attachment):
    def __init__(self, token: str):
        Attachment.__init__(self, type='split', token=token)

    @property
    def token(self):
        return self._kwargs.get('token')


class EmojiAttachment(Attachment):
    def __init__(self, placeholder: str, charmap: List[List[Union[int, int]]]):
        Attachment.__init__(self, type='emoji', placeholder=placeholder, charmap=charmap)

    @property
    def placeholder(self):
        return self._kwargs.get('placeholder')


class MentionsAttachment(Attachment):
    def __init__(self, loci: List[List[int]], user_ids: List[int]):
        Attachment.__init__(self, type='mentions', loci=loci, user_ids=user_ids)

    @property
    def loci(self):
        return self._kwargs.get('loci')

    @property
    def user_ids(self):
        return self._kwargs.get('user_ids')


def parse_attachment(attachment_dict: dict) -> Attachment:
    attachment_type = attachment_dict.get('type')
    if attachment_type is None:
        raise InvalidAttachment('`type` key not present')

    if attachment_type == 'image':
        return ImageAttachment(attachment_dict.get('url'))
    elif attachment_type == 'location':
        return LocationAttachment(attachment_dict.get('name'), attachment_dict.get('lat'), attachment_dict.get('lng'))
    elif attachment_type == 'split':
        return SplitAttachment(attachment_dict.get('token'))
    elif attachment_type == 'emoji':
        return EmojiAttachment(attachment_dict.get('placeholder'), attachment_dict.get('charmap'))
    elif attachment_type == 'mentions':
        return MentionsAttachment(attachment_dict.get('loci'), attachment_dict.get('user_ids'))

    raise InvalidAttachment(f'unsupported attachment type `{attachment_type}`')
