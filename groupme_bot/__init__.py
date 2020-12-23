"""
groupme-bot

A simple bot builder for GroupMe
"""
from .bot import Bot, Context
from .router import Router
from .callback import Callback
from .attachment import ImageAttachment, LocationAttachment, SplitAttachment, EmojiAttachment, MentionsAttachment

__version__ = "0.1.5"
__author__ = "Branden Colen"
__all__ = [
    "Bot", "Router", "Callback", "Context",
    "ImageAttachment", "LocationAttachment",
    "SplitAttachment", "EmojiAttachment",
    "MentionsAttachment"
]
