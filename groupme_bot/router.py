import atexit

from waitress import serve
from flask import request, Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler

from .bot import Bot
from .callback import Callback


class RouteExistsError(Exception):
    pass


class Router:
    _bot_summary = {}

    def __init__(self, flask_app: Flask = None):
        self._app = flask_app if flask_app else Flask(__name__)
        self._cron = BackgroundScheduler(daemon=True)

    def add_bot(self, bot: Bot, callback_route: str):
        endpoint = callback_route.replace("/", "") + '-callback-handler'

        @self._app.route(callback_route, endpoint=endpoint, methods=['POST'])
        def callback_handler():
            request_data = request.get_json(silent=True)
            bot.handle_callback(Callback(request_data))

        for args, kwargs, func in bot.iter_cron_jobs():
            self._cron.add_job(func, 'cron', *args, **kwargs)

        self._bot_summary[callback_route] = bot.bot_name

    def run(self, host: str = "0.0.0.0", port: int = 8000, debug: bool = True):
        @self._app.route('/', methods=['GET'])
        def index():
            job_summary = []
            jobs = self._cron.get_jobs()
            if jobs:
                for job in jobs:
                    job_summary.append(str(job))
            return jsonify({'endpoints': self._bot_summary, 'jobs': job_summary})

        # start the cron scheduler and setup a shutdown on exit
        self._cron.start()
        atexit.register(lambda: self._cron.shutdown(wait=False))

        # run the flask app
        if debug:
            self._app.run(host=host, port=port, debug=debug)
        else:
            serve(self._app, host=host, port=port)
