"""
groupme-bot

A simple bot builder for GroupMe
"""
from .bot import Bot
from .router import Router
from .callback import Callback
from .attachment import ImageAttachment, LocationAttachment, SplitAttachment, EmojiAttachment

__version__ = "0.1.0"
__author__ = "Branden Colen"
__all__ = [
    "Bot", "Router", "Callback",
    "ImageAttachment", "LocationAttachment",
    "SplitAttachment", "EmojiAttachment"
]
