import json
import re
from typing import Any, List

import requests

from .attachment import Attachment, MentionsAttachment
from .callback import Callback

BOT_INDEX_URL = 'https://api.groupme.com/v3/bots'
BOT_POST_URL = 'https://api.groupme.com/v3/bots/post'
GROUP_ME_IMAGES_URL = 'https://image.groupme.com/pictures'
GROUPS_URL = 'https://api.groupme.com/v3/groups/'


class HandlerPatternExistsError(Exception):
    pass


class Bot:
    _handler_functions = {}
    _cron_functions = []

    def __init__(self, bot_name: str, bot_id: str, api_token: str, group_id: str):
        self.bot_name = bot_name
        self.bot_id = bot_id
        self.api_token = api_token
        self.group_id = group_id

    def __str__(self):
        return "Bot Name: %s, # Handlers: %d, # Cron Tasks: %d" % \
               (self.bot_name, len(self._handler_functions), len(self._cron_functions))

    def callback_handler(self, regex_pattern: str):
        """A decorator that is used to register a regex pattern as to a bot handler function. If the regex pattern
        is found in a message from a GroupMe user, the function will be called.

        :param regex_pattern: The pattern to search for in the message text
        """
        def decorator(f):
            if regex_pattern in self._handler_functions:
                raise HandlerPatternExistsError(
                    "The pattern `" + regex_pattern + "` is already registered to a handler")
            self._handler_functions[regex_pattern] = f
            return f
        return decorator

    def cron_task(self, *args, **kwargs):
        """A decorator that registers a function to be run on set cron schedule
        
        Available arguments (https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html):
            - year (int|str) – 4-digit year
            - month (int|str) – month (1-12)
            - day (int|str) – day of the (1-31)
            - week (int|str) – ISO week (1-53)
            - day_of_week (int|str) – number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
            - hour (int|str) – hour (0-23)
            - minute (int|str) – minute (0-59)
            - second (int|str) – second (0-59)
            - start_date (datetime|str) – earliest possible date/time to trigger on (inclusive)
            - end_date (datetime|str) – latest possible date/time to trigger on (inclusive)
            - timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations (defaults to scheduler timezone)
            - jitter (int|None) – advance or delay the job execution by jitter seconds at most.
        """
        def decorator(f):
            self._cron_functions.append({'args': args, 'kwargs': kwargs, 'f': f})
            return f
        return decorator

    def iter_cron_jobs(self):
        for job in self._cron_functions:
            yield job['args'], job['kwargs'], job['f']

    def handle_callback(self, callback: Callback) -> Any:
        if callback.is_from_user():
            text = callback.text.lower().strip()
            for pattern, func in self._handler_functions.items():
                if re.search(pattern, text):
                    return func(callback)

    def post_message(self, msg: str, attachments: List[Attachment] = None) -> requests.Response:
        """Posts a bot message to the group with optional attachments.

        :param str msg: The message to be sent
        :param List[dict] attachments: (optional) Attachments to send in the message
        :return requests.Response: The POST request response object
        """
        data = {
            "bot_id": self.bot_id,
            "text": msg,
            "attachments": [attachment.to_dict() for attachment in attachments]
        }
        response = requests.post(BOT_POST_URL, data=json.dumps(data), headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return response

    def image_url_to_groupme_image_url(self, image_url: str) -> str:
        """Convert a normal image URL to a GroupMe image to allow for usage as an attachment

        :param str image_url: The URL for any image
        :return str: The URL for the converted GroupMe image
        """
        r = requests.get(image_url)
        r.raise_for_status()
        headers = {
            'X-Access-Token': self.api_token,
            'Content-Type': r.headers['Content-type'],
        }
        response = requests.post(GROUP_ME_IMAGES_URL, headers=headers, data=r.content)
        response.raise_for_status()
        out = response.json()
        return out['payload']['picture_url']

    def get_group_summary(self) -> dict:
        """Get the summary of the group"""
        out = requests.get(GROUPS_URL + self.group_id, params={'token': self.api_token})
        out.raise_for_status()
        return out.json()['response']

    def mention_all(self) -> None:
        """Mentions everybody in the group so they receive a notification"""
        text = ''
        user_ids = []
        loci = []
        for member in self.get_group_summary()['members']:
            user_ids.append(member['user_id'])
            loci.append([len(text), len(member['nickname']) + 1])
            text += '@{} '.format(member['nickname'])
        self.post_message(text, [MentionsAttachment(loci=loci, user_ids=user_ids)])
