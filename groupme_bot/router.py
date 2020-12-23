import atexit
import logging
from typing import Any, List

from waitress import serve
from flask import request, Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler, BaseScheduler

from .bot import Bot, Context
from .callback import Callback


class RouteExistsError(Exception):
    pass


class Router(object):
    def __init__(self, flask_app: Flask = None, scheduler: BaseScheduler = None):
        """
        The Router is the primary object used to run the GroupMe Bot. Multiple Bots can be handled in one single
        router object. Each bot is assigned an endpoint path and requests to that endpoint will be handled by the
        associated bot.

        :param Flask flask_app: (optional) Default to Flask(__name__)
        :param BaseScheduler scheduler: (optional) Default to BackgroundScheduler(daemon=True)
        """
        self._app = flask_app if flask_app else Flask(__name__)
        self._scheduler = scheduler if scheduler else BackgroundScheduler(daemon=True)
        # build an memory store for bot objects
        self._bots = {}
        # add app summary to index page
        self._app.add_url_rule('/', 'index', self._summarize, methods=['GET'])
        # define a logger
        self._logger = logging.Logger('Router')
        self._logger.setLevel(logging.INFO)

    @property
    def bot_store(self) -> dict[str, Bot]:
        """
        The current store of routes and the associated bot.
        :return dict[str, Bot]: key=the endpoint route, value=the bot object associated
        """
        return self._bots

    @property
    def flask_app(self) -> Flask:
        """
        The Flask app objects being used for the router.
        :return Flask:
        """
        return self._app

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
    def endpoints(self) -> dict[str, str]:
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
        # store the bot for later access
        self._bots[callback_path] = bot

        # add the flask route
        self._app.add_url_rule(
            callback_path,
            callback_path.replace("/", "") + '-callback-handler',
            self._handle_callback,
            methods=['POST']
        )

        # add scheduler jobs
        for job in bot.cron_jobs:
            self._scheduler.add_job(
                job['func'],
                job['trigger'],
                args=(Context(bot, Callback({})), ),
                **job['kwargs']
            )

    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False) -> None:
        """Run the Router with all bot handlers and scheduled jobs.

        :param str host:
        :param int port:
        :param bool debug:
        """
        # start the cron scheduler and setup a shutdown on exit
        self._scheduler.start()
        atexit.register(lambda: self._scheduler.shutdown(wait=False))

        # run the flask app
        if debug:
            self._app.run(host=host, port=port, debug=debug)
        else:
            self._logger.setLevel(logging.ERROR)
            serve(self._app, host=host, port=port)

    def _summarize(self) -> Any:
        return jsonify({'endpoints': self.endpoints, 'jobs': self.jobs})

    def _handle_callback(self) -> str:
        request_data = request.get_json(silent=True)
        ctx = Context(self._bots[request.path], Callback(request_data))
        bot = self._bots[request.path]
        try:
            bot.handle_callback(ctx)
            self._logger.info({'status': 'SUCCESS', 'bot': str(bot), 'request': request_data})
            return 'Success'
        except Exception as e:
            self._logger.error({'status': 'ERROR', 'bot': str(bot), 'request': request_data}, exc_info=e)
            return str(e)
