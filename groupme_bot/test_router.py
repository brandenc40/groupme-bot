from unittest import TestCase

from .bot import Bot
from .router import Router, RouteExistsError


class TestRouter(TestCase):

    def test_add_bot(self):
        router = Router()

        with self.assertRaises(RouteExistsError):
            router.add_bot(Bot("", "", "", ""), '/_health')

        with self.assertRaises(RouteExistsError):
            router.add_bot(Bot("", "", "", ""), '/')

        router.add_bot(Bot("fake", "", "", ""), "/bot")
        self.assertEqual(list(router.bot_store.keys()), ['/bot'])
        self.assertIsInstance(router.bot_store['/bot'], Bot)
