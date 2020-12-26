import atexit
import logging
from json.decoder import JSONDecodeError
from typing import List, Callable, Dict

from apscheduler.schedulers.background import BackgroundScheduler, BaseScheduler
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.types import Scope, Receive, Send

from .bot import Bot, Context
from .callback import Callback

_not_allowed = PlainTextResponse('405 Method Not Allowed', status_code=405)
_not_found = PlainTextResponse('404 Not Found', status_code=404)


class RouteExistsError(Exception):
    pass


class Application(object):
    __slots__ = ('_scheduler', '_bots', '_logger')
    _reserved_routes = ('/', '/_health')

    def __init__(self, scheduler: BaseScheduler = None):
        """
        The Router is the primary object used to run the GroupMe Bot. Multiple Bots can be handled in one single
        router object. Each bot is assigned an endpoint path and requests to that endpoint will be handled by the
        associated bot.

        :param BaseScheduler scheduler: (optional) Default to BackgroundScheduler(daemon=True)
        """
        # start the cron scheduler and setup a shutdown on exit
        self._scheduler = scheduler if scheduler else BackgroundScheduler(daemon=True)
        self._scheduler.start()
        atexit.register(lambda: self._scheduler.shutdown(wait=False))

        # build an memory store for bot objects
        self._bots = {}

        # define a logger
        self._logger = logging.Logger(__name__)
        self._logger.setLevel(logging.INFO)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        req = Request(scope, receive, send)
        path = req.url.path

        if path in self._bots:
            if req.method != 'POST':
                await _not_allowed(scope, receive, send)
            else:
                try:
                    callback_dict = await req.json()
                except JSONDecodeError as e:
                    response = PlainTextResponse(
                        "400 Bad Request. Unable to parse JSON. Error: " + str(e), status_code=400)
                    await response(scope, receive, send)
                else:
                    bot = self._bots[path]
                    try:
                        bot.handle_callback(Context(bot, Callback(callback_dict)))
                        self._logger.info({'status': 'SUCCESS', 'bot': str(bot), 'request': callback_dict})
                        response = PlainTextResponse('Success')
                    except Exception as e:
                        self._logger.error({'status': 'ERROR', 'bot': str(bot), 'request': callback_dict}, exc_info=e)
                        response = PlainTextResponse(str(e))
                    await response(scope, receive, send)

        elif path == '/':
            if req.method != 'GET':
                await _not_allowed(scope, receive, send)
            else:
                response = JSONResponse({'endpoints': self.endpoints, 'jobs': self.jobs})
                await response(scope, receive, send)

        elif path == '/_health':
            if req.method != 'GET':
                await _not_allowed(scope, receive, send)
            else:
                response = PlainTextResponse('OK')
                await response(scope, receive, send)
        else:
            await _not_found(scope, receive, send)

    @property
    def bot_store(self) -> Dict[str, Bot]:
        """
        The current store of routes and the associated bot.
        :return dict[str, Bot]: key=the endpoint route, value=the bot object associated
        """
        return self._bots

    @property
    def scheduler(self) -> BaseScheduler:
        """
        The BaseScheduler object being used for cron jobs
        :return BaseScheduler:
        """
        return self._scheduler

    @property
    def logger(self) -> logging.Logger:
        """
        The Logger being used
        :return logging.Logger:
        """
        return self._logger

    @property
    def endpoints(self) -> Dict[str, str]:
        """
        A summary of all endpoints within the Router
        :return dict[str, str]: key=the endpoint path, value=the string repr of the associated Bot
        """
        endpoint_summary = {}
        for path, bot in self._bots.items():
            endpoint_summary[path] = str(bot)
        return endpoint_summary

    @property
    def jobs(self) -> List[str]:
        """
        A list of all currently running scheduler jobs
        :return List[str]: A list of the string repr of each running job
        """
        job_summary = []
        jobs = self._scheduler.get_jobs()
        if jobs:
            for job in jobs:
                job_summary.append(str(job))
        return job_summary

    def add_bot(self, bot: Bot, callback_path: str) -> None:
        """Add a new bot to be run by the Router

        :param bot: The bot to be run
        :param callback_path: The callback path for which the bot can be accesses
        :return:
        """
        # perform validity checks
        if callback_path in self._reserved_routes:
            raise RouteExistsError(
                'Cannot use one of the reserved routes. Reserved routes are: ' + str(self._reserved_routes))

        if callback_path in self._bots:
            raise RouteExistsError(
                "Callback path `{}` is already in use by a separate bot. Must use a new route for each bot."
                    .format(callback_path))

        # store the bot for later access
        self._bots[callback_path] = bot

        # add scheduler jobs
        for job in bot.cron_jobs:
            self._scheduler.add_job(
                job['func'],
                job['trigger'],
                args=(Context(bot, Callback({})),),
                **job['kwargs']
            )
