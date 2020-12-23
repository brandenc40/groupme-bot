from typing import List, Union


class Attachment:
    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def to_dict(self):
        out = {}
        for key, value in self._kwargs.items():
            if key in ('charmap', 'loci', 'user_ids'):
                out[key] = value if value else []
            else:
                out[key] = str(value)
        return out


class ImageAttachment(Attachment):
    def __init__(self, image_url: str):
        Attachment.__init__(self, type='image', url=image_url)


class LocationAttachment(Attachment):
    def __init__(self, name: str, lat: Union[str, float, int], lng: Union[str, float, int]):
        Attachment.__init__(self, type='location', name=name, lat=lat, lng=lng)


class SplitAttachment(Attachment):
    def __init__(self, token: str):
        Attachment.__init__(self, type='split', token=token)


class EmojiAttachment(Attachment):
    def __init__(self, placeholder: str, charmap: List[List[Union[int, int]]]):
        Attachment.__init__(self, type='emoji', placeholder=placeholder, charmap=charmap)


class MentionsAttachment(Attachment):
    def __init__(self, loci: List[List[int]], user_ids: List[int]):
        Attachment.__init__(self, type='mentions', loci=loci, user_ids=user_ids)
