"""
groupme-bot

A simple bot builder for GroupMe
"""
from .application import Application
from .attachment import ImageAttachment, LocationAttachment, SplitAttachment, EmojiAttachment, MentionsAttachment
from .bot import Bot, Context
from .callback import Callback

__version__ = "0.2.0"
__author__ = "Branden Colen"
__all__ = [
    "Bot", "Application", "Callback", "Context",
    "ImageAttachment", "LocationAttachment",
    "SplitAttachment", "EmojiAttachment",
    "MentionsAttachment"
]
