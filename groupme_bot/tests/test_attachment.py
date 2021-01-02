from unittest import TestCase

from ..attachment import (
    InvalidAttachment, ImageAttachment, LocationAttachment,
    SplitAttachment, EmojiAttachment, MentionsAttachment,
    parse_attachment
)


class Test(TestCase):
    def test_parse_attachment(self):
        a = {
            'url': '',
            'name': '',
            'lat': '',
            'lng': '',
            'token': '',
            'placeholder': '',
            'charmap': '',
            'user_ids': '',
            'loci': ''
        }

        with self.assertRaises(InvalidAttachment):
            parse_attachment(a)

        a['type'] = 'fake'
        with self.assertRaises(InvalidAttachment):
            parse_attachment(a)

        a['type'] = 'image'
        o = parse_attachment(a)
        self.assertIsInstance(o, ImageAttachment)

        a['type'] = 'location'
        o = parse_attachment(a)
        self.assertIsInstance(o, LocationAttachment)

        a['type'] = 'split'
        o = parse_attachment(a)
        self.assertIsInstance(o, SplitAttachment)

        a['type'] = 'emoji'
        o = parse_attachment(a)
        self.assertIsInstance(o, EmojiAttachment)

        a['type'] = 'mentions'
        o = parse_attachment(a)
        self.assertIsInstance(o, MentionsAttachment)
