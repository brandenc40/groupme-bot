import json
import re
from typing import Any, List, Callable

import requests

from .attachment import Attachment, MentionsAttachment
from .context import Context

BASE_URL = 'https://api.groupme.com/v3'
BOT_INDEX_URL = BASE_URL + '/bots'
BOT_POST_URL = BASE_URL + '/bots/post'
GROUPS_URL = BASE_URL + '/groups/'
GROUP_ME_IMAGES_URL = 'https://image.groupme.com/pictures'


class HandlerPatternExistsError(Exception):
    pass


class Bot(object):
    def __init__(self, bot_name: str, bot_id: str, groupme_api_token: str, group_id: str):
        """
        The Bot class represents a single bot that can contains multiple callback handlers and scheduled jobs.
        Bots are run using the Router class.

        :param bot_name: A unique name for this bot to be known as within this code. Does not impact the name
            displayed in the GroupMe app.
        :param bot_id: The Bot ID provided by GroupMe.
        :param groupme_api_token: The GroupMe API token for access to group details.
        :param group_id: The id of the GroupMe group in which the bot exists.
        """
        self.bot_name = bot_name
        self.bot_id = bot_id
        self.api_token = groupme_api_token
        self.group_id = group_id

        self._handler_functions = {}
        self._cron_jobs = []

    @property
    def cron_jobs(self) -> List[dict]:
        """
        All list of cron jobs associated with this bot.

        :return List[dict]:
        """
        return self._cron_jobs

    def __str__(self):
        return "%s: %d callback handlers, %d cron jobs" \
               % (self.bot_name, len(self._handler_functions), len(self._cron_jobs))

    def add_callback_handler(self, regex_pattern: str, func: Callable[[Context], Any]) -> None:
        """
        Registers a regex pattern as to a bot handler function. If the regex pattern
        is found in a message from a GroupMe user, the function will be called.

        :param regex_pattern: The pattern to search for in the message text
        :param Callable[[Context], Any] func: The function to be called when the pattern is matched
        """
        if regex_pattern in self._handler_functions:
            raise HandlerPatternExistsError("The pattern `%s` is already registered to a handler" % regex_pattern)
        self._handler_functions[regex_pattern] = func

    def add_cron_job(self, func: Callable[[Context], Any], **kwargs) -> None:
        """
        Registers a function to be run on set cron schedule.
        
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

        :param Callable[[Context], Any] func: The function to be called when the cron trigger is triggered
        """
        self._cron_jobs.append({
            'func': func,
            'trigger': 'cron',
            'kwargs': kwargs
        })

    def handle_callback(self, ctx: Context) -> None:
        """
        The main method used to handle incoming messages. Callbacks will not be handled if they are messages that came
        from the bot itself to prevent infinite loops.

        :param Context ctx: The Context of the request containing the Callback and the Bot objects.
        """
        if ctx.callback.user_id == self.bot_id:
            return
        text = ctx.callback.text.lower().strip()
        for pattern, func in self._handler_functions.items():
            if re.search(pattern, text):
                func(ctx)

    def post_message(self, msg: str, attachments: List[Attachment] = None) -> requests.Response:
        """
        Posts a bot message to the group with optional attachments.

        :param str msg: The message to be sent
        :param List[Attachment] attachments: (optional) Attachments to send in the message
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
        """
        Get a summary of the group from the GroupMe API

        :return dict:
        """
        out = requests.get(GROUPS_URL + self.group_id, params={'token': self.api_token})
        out.raise_for_status()
        return out.json()['response']

    def mention_all(self) -> None:
        """
        Mentions everybody in the group so they receive a notification
        """
        text = ''
        user_ids = []
        loci = []
        for member in self.get_group_summary()['members']:
            user_ids.append(member['user_id'])
            loci.append([len(text), len(member['nickname']) + 1])
            text += '@{} '.format(member['nickname'])
        self.post_message(text, [MentionsAttachment(loci=loci, user_ids=user_ids)])
