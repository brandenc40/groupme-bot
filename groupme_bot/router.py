import atexit

from waitress import serve
from flask import request, Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler, BaseScheduler

from .context import Context
from .bot import Bot
from .callback import Callback


class RouteExistsError(Exception):
    pass


class Router(object):
    def __init__(self, flask_app: Flask = None, scheduler: BaseScheduler = None):
        self._app = flask_app if flask_app else Flask(__name__)
        self._scheduler = scheduler if scheduler else BackgroundScheduler(daemon=True)

        self._bots = dict()
        self._jobs = list()

    def _summarize(self):
        job_summary = []
        jobs = self._scheduler.get_jobs()
        if jobs:
            for job in jobs:
                job_summary.append(str(job))

        bot_summary = {}
        for path, bot in self._bots.items():
            bot_summary[path] = str(bot)

        return jsonify({'endpoints': bot_summary, 'jobs': job_summary})

    def add_bot(self, bot: Bot, callback_route: str):
        self._bots[callback_route] = bot
        for job in bot.cron_jobs:
            self._jobs.append({"bot": bot, "job": job})

    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = False):
        # add app summary to index page
        self._app.add_url_rule('/', 'index', self._summarize, methods=['GET'])

        def callback_handler():
            request_data = request.get_json(silent=True)
            ctx = Context(self._bots[request.path], Callback(request_data))
            try:
                self._bots[request.path].handle_callback(ctx)
                return 'Success'
            except Exception as e:
                return 'Error: ' + str(e)

        # add routes to be handled
        for route in self._bots.keys():
            self._app.add_url_rule(
                route,
                route.replace("/", "") + '-callback-handler',
                callback_handler,
                methods=['POST']
            )

        # add scheduler jobs
        for job in self._jobs:
            self._scheduler.add_job(
                job['job']['func'],
                job['job']['trigger'],
                args=(Context(job['bot'], Callback({})), ),
                **job['job']['kwargs'])

        # start the cron scheduler and setup a shutdown on exit
        self._scheduler.start()
        atexit.register(lambda: self._scheduler.shutdown(wait=False))

        # run the flask app
        if debug:
            self._app.run(host=host, port=port, debug=debug)
        else:
            serve(self._app, host=host, port=port)
