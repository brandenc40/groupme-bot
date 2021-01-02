from unittest import TestCase

from ..callback import Callback


class TestCallback(TestCase):
    def test_attachments(self):
        c_dict = {
            "attachments": [
                {
                    "type": "location",
                    "lng": "40.000",
                    "lat": "70.000",
                    "name": "GroupMe HQ"
                },
                {
                    "type": "image",
                    "url": "https://i.groupme.com/somethingsomething.large"
                }
            ],
            "avatar_url": "https://i.groupme.com/123456789",
            "created_at": 1302623328,
            "group_id": "1234567890",
            "id": "1234567890",
            "name": "John",
            "sender_id": "12345",
            "sender_type": "user",
            "source_guid": "GUID",
            "system": False,
            "text": "Hello world ☃☃",
            "user_id": "1234567890"
        }
        c = Callback(c_dict)
        self.assertEqual(c.attachments[0].type, 'location')
        self.assertEqual(c.attachments[1].type, 'image')
        self.assertEqual(c.avatar_url, 'https://i.groupme.com/123456789')
        self.assertEqual(c.created_at, 1302623328)
        self.assertEqual(c.group_id, '1234567890')
        self.assertEqual(c.id, '1234567890')
        self.assertEqual(c.name, 'John')
        self.assertEqual(c.sender_id, '12345')
        self.assertEqual(c.sender_type, 'user')
        self.assertEqual(c.source_guid, 'GUID')
        self.assertEqual(c.system, False)
        self.assertEqual(c.text, 'Hello world ☃☃')
        self.assertEqual(c.user_id, '1234567890')
