from __future__ import annotations

import re
from collections import OrderedDict
from json.decoder import JSONDecodeError
from typing import Any, List, Callable, Optional

import httpx
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.types import Scope, Receive, Send

from .attachment import Attachment, MentionsAttachment
from .callback import Callback
from .groupme import GroupMe

_success_response = PlainTextResponse('Success')


class HandlerPatternExistsError(Exception):
    pass


class Context(object):
    __slots__ = ('_bot', '_callback')

    def __init__(self, bot: Bot, callback: Callback):
        """
        Context provided to every handler/scheduled function run by the bot. This provides a clean object containing
        bot the bot in use and the Callback that was sent.
        :param Bot bot:
        :param Callback callback:
        """
        self._bot: Bot = bot
        self._callback: Callback = callback

    @property
    def bot(self) -> Bot:
        return self._bot

    @property
    def callback(self) -> Callback:
        return self._callback


class Bot(GroupMe):
    __slots__ = ('bot_name', 'bot_id', 'groupme_api_token', 'group_id', '_handler_functions', '_jobs')

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
        super().__init__(groupme_api_token)
        self.bot_name = bot_name
        self.bot_id = bot_id
        self.groupme_api_token = groupme_api_token
        self.group_id = group_id

        self._handler_functions: OrderedDict = OrderedDict()
        self._jobs = []

    @property
    def cron_jobs(self) -> List[dict]:
        """
        All list of cron jobs associated with this bot.
        :return List[dict]:
        """
        return self._jobs

    def __str__(self):
        return f"{self.bot_name}: {len(self._handler_functions)} callback handlers, " \
               f"{len(self._jobs)} cron jobs at {hex(id(self))}"

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        req = Request(scope, receive, send)
        try:
            callback_dict = await req.json()
        except JSONDecodeError as e:
            response = PlainTextResponse(
                "400 Bad Request. Unable to parse JSON. Error: " + str(e), status_code=400)
            await response(scope, receive, send)
            return
        callback = Callback(callback_dict)
        if callback.sender_type != 'user':  # only reply to users
            await _success_response(scope, receive, send)
            return
        text = callback.text.lower().strip()
        for pattern, func in self._handler_functions.items():
            if re.search(pattern, text):
                try:
                    func(Context(self, callback))
                    await _success_response(scope, receive, send)
                    return
                except Exception as e:
                    response = PlainTextResponse(str(e), status_code=500)
                    await response(scope, receive, send)
                    return
        await _success_response(scope, receive, send)
        return

    def add_callback_handler(self, regex_pattern: str, func: Callable[[Context], Any]) -> None:
        """
        Registers a regex pattern as to a bot handler function. If the regex pattern
        is found in a message from a GroupMe user, the function will be called.
        :param regex_pattern: The pattern to search for in the message text
        :param Callable[[Context], Any] func: The function to be called when the pattern is matched
        """
        if regex_pattern in self._handler_functions:
            raise HandlerPatternExistsError(f"The pattern `{regex_pattern}` is already registered to a handler")
        self._handler_functions[regex_pattern] = func

    def add_cron_job(self, func: Callable[[Context], Any], **kwargs) -> None:
        """
        Registers a function to be run on set cron schedule.
        Uses APScheduler cron trigger. Details here:
            https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
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
            - timezone (datetime.tzinfo|str) – time zone to use for the date/time calculations
                (defaults to scheduler timezone)
            - jitter (int|None) – advance or delay the job execution by jitter seconds at most.
        :param Callable[[Context], Any] func: The function to be called when the cron trigger is triggered
        """
        self._jobs.append({
            'func': func,
            'trigger': 'cron',
            'args': (Context(self, Callback({})),),
            'kwargs': kwargs
        })

    def post_message(self, msg: str, attachments: Optional[List[Attachment]] = None) -> httpx.Response:
        """
        Posts a bot message to the group with optional attachments.
        :param str msg: The message to be sent
        :param Optional[List[Attachment]] attachments: Attachments to send in the message
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
        response = httpx.post(
            'https://api.groupme.com/v3/bots/post',
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response

    def mention_all(self) -> None:
        """
        Mentions everybody in the group so they receive a notification
        """
        text = ''
        user_ids = []
        loci = []
        group = self.get_group(self.group_id)
        for member in group['members']:
            user_ids.append(member['user_id'])
            loci.append([len(text), len(member['nickname']) + 1])
            text += '@{} '.format(member['nickname'])
        self.post_message(text, [MentionsAttachment(loci=loci, user_ids=user_ids)])
