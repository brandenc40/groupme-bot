"""
groupme-bot

A simple bot builder for GroupMe
"""
from .bot import Bot
from .router import Router
from .callback import Callback
from .context import Context
from .attachment import ImageAttachment, LocationAttachment, SplitAttachment, EmojiAttachment, MentionsAttachment

__version__ = "0.1.2"
__author__ = "Branden Colen"
__all__ = [
    "Bot", "Router", "Callback", "Context",
    "ImageAttachment", "LocationAttachment",
    "SplitAttachment", "EmojiAttachment",
    "MentionsAttachment"
]
