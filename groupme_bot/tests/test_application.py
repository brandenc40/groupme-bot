from unittest import TestCase

from ..bot import Bot
from ..application import Application, RouteExistsError


class TestRouter(TestCase):

    def test_add_bot(self):
        app = Application()

        with self.assertRaises(RouteExistsError):
            app.add_bot(Bot("", "", "", ""), '/_health')

        with self.assertRaises(RouteExistsError):
            app.add_bot(Bot("", "", "", ""), '/')

        app.add_bot(Bot("fake", "", "", ""), "/bot")
        self.assertEqual(list(app.bot_store.keys()), ['/bot'])
        self.assertIsInstance(app.bot_store['/bot'], Bot)
