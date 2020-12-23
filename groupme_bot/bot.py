import json
import re
from typing import Any, List

import requests

from .attachment import Attachment, MentionsAttachment
from .context import Context

BOT_INDEX_URL = 'https://api.groupme.com/v3/bots'
BOT_POST_URL = 'https://api.groupme.com/v3/bots/post'
GROUP_ME_IMAGES_URL = 'https://image.groupme.com/pictures'
GROUPS_URL = 'https://api.groupme.com/v3/groups/'


class HandlerPatternExistsError(Exception):
    pass


class Bot(object):
    def __init__(self, bot_name: str, bot_id: str, groupme_api_token: str, group_id: str):
        self.bot_name = bot_name
        self.bot_id = bot_id
        self.api_token = groupme_api_token
        self.group_id = group_id

        self._handler_functions = {}
        self._cron_jobs = []

    def __str__(self):
        return "Bot Name: %s, # Handlers: %d, # Cron Tasks: %d" % \
               (self.bot_name, len(self._handler_functions), len(self._cron_jobs))

    @property
    def cron_jobs(self) -> List[dict]:
        return self._cron_jobs

    def add_callback_handler(self, regex_pattern: str, func: Any):
        """Registers a regex pattern as to a bot handler function. If the regex pattern
        is found in a message from a GroupMe user, the function will be called.

        :param regex_pattern: The pattern to search for in the message text
        :param Callable func: The function to be called when the pattern is matched
        """
        if regex_pattern in self._handler_functions:
            raise HandlerPatternExistsError(
                "The pattern `" + regex_pattern + "` is already registered to a handler")
        self._handler_functions[regex_pattern] = func

    def add_cron_task(self, func: Any, **kwargs) -> None:
        """Registers a function to be run on set cron schedule.
        
        Uses APScheduler cron trigger. Details here: https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
        
        Available arguments:
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

        :param Callable func: The function to be called when the cron trigger is triggered
        """
        self._cron_jobs.append({
            'func': func,
            'trigger': 'cron',
            'kwargs': kwargs
        })

    def handle_callback(self, ctx: Context) -> Any:
        if ctx.callback.is_from_user():
            text = ctx.callback.text.lower().strip()
            for pattern, func in self._handler_functions.items():
                if re.search(pattern, text):
                    return func(ctx)

    def post_message(self, msg: str, attachments: List[Attachment] = None) -> requests.Response:
        """Posts a bot message to the group with optional attachments.

        :param str msg: The message to be sent
        :param List[dict] attachments: (optional) Attachments to send in the message
        :return requests.Response: The POST request response object
        """
        if attachments:
            attachments = [attachment.to_dict() for attachment in attachments]
        else:
            attachments = []
        data = {
            "bot_id": self.bot_id,
            "text": msg,
            "attachments": attachments
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
        """Get a summary of the group"""
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
