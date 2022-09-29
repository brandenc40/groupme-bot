import atexit
from typing import List, Dict

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from starlette.requests import Request
from starlette.responses import PlainTextResponse, JSONResponse
from starlette.types import Scope, Receive, Send, ASGIApp

from .bot import Bot

GET = 'GET'
POST = 'POST'
HEAD = 'HEAD'

_not_allowed = PlainTextResponse('405 Method Not Allowed', status_code=405)
_not_found = PlainTextResponse('404 Not Found', status_code=404)
_ping_handler = PlainTextResponse('Hello', status_code=200)


class RouteExistsError(Exception):
    pass


class Application(object):
    __slots__ = ('_scheduler', '_route_tree')
    _reserved_routes = ('/', '/_health')

    def __init__(self):
        """
        The Router is the primary object used to run the GroupMe Bot. Multiple Bots can be handled in one single
        router object. Each bot is assigned an endpoint path and requests to that endpoint will be handled by the
        associated bot.
        """
        self._scheduler: AsyncIOScheduler = AsyncIOScheduler()

        async def _summary(scope: Scope, receive: Receive, send: Send):
            response = JSONResponse({
                'endpoints': self.endpoints,
                'jobs': self.jobs,
                'scheduler_running': self._scheduler.running
            })
            await response(scope, receive, send)

        async def _health(scope: Scope, receive: Receive, send: Send):
            response = PlainTextResponse('OK')
            await response(scope, receive, send)

        self._route_tree: Dict[str, Dict[str, ASGIApp]] = {
            '/': {GET: _summary, HEAD: _ping_handler},
            '/_health': {GET: _health}
        }

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        req = Request(scope, receive, send)
        path = self._route_tree.get(req.url.path)
        if not path:
            await _not_found(scope, receive, send)
            return
        handler = path.get(req.method)
        if not handler:
            await _not_allowed(scope, receive, send)
            return
        await handler(scope, receive, send)

    def _start_scheduler(self):
        atexit.register(lambda: self._scheduler.shutdown(wait=False))
        self._scheduler.start()

    @property
    def routes(self) -> Dict[str, Dict[str, ASGIApp]]:
        """
        The current store of routes and the associated bot.
        :return dict[str, Bot]: key=the endpoint route, value=the bot object associated
        """
        return self._route_tree

    @property
    def scheduler(self) -> AsyncIOScheduler:
        """
        The AsyncIOScheduler object being used for cron jobs
        :return AsyncIOScheduler:
        """
        return self._scheduler

    @property
    def endpoints(self) -> Dict[str, Dict[str, str]]:
        """
        A summary of all endpoints within the Router
        """
        endpoint_summary = {}
        for path, methods in self._route_tree.items():
            for method, handler in methods.items():
                str_repr = handler.__name__ if hasattr(handler, '__name__') else str(handler)
                if endpoint_summary.get('path'):
                    endpoint_summary[path][method] = str_repr
                else:
                    endpoint_summary[path] = str_repr
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
        """
        Add a new bot to be run by the Router
        :param bot: The bot to be run
        :param callback_path: The callback path for which the bot can be accesses
        :return:
        """
        # perform validity checks
        if callback_path in self._reserved_routes:
            raise RouteExistsError(f'Cannot use one of the reserved routes. Reserved '
                                   f'routes are: {str(self._reserved_routes)}')

        if callback_path in self._route_tree:
            raise RouteExistsError(f"Callback path `{callback_path}` is already in use. "
                                   f"You must use a new route for each bot.")

        # store the bot for call routing
        self._route_tree[callback_path] = {POST: bot, GET: _ping_handler, HEAD: _ping_handler}

        # add any scheduler jobs
        for job in bot.cron_jobs:
            self._scheduler.add_job(
                job['func'],
                job['trigger'],
                args=job['args'],
                **job['kwargs']
            )
            if not self._scheduler.running:
                self._start_scheduler()
