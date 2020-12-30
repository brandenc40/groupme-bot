from unittest import TestCase

from ..bot import Bot
from ..application import Application, RouteExistsError


class TestRouter(TestCase):

    def test_add_bot(self):
        app = Application()

        bot = Bot("", "", "", "")

        with self.assertRaises(RouteExistsError):
            app.add_bot(bot, '/_health')

        with self.assertRaises(RouteExistsError):
            app.add_bot(bot, '/')

        app.add_bot(bot, "/bot")
        self.assertEqual(list(app.routes.keys()), ['/', '/_health', '/bot'])
        self.assertIsInstance(app.routes['/bot']['POST'], Bot)
