import asyncio
import logging
import pathlib

import jinja2

import aiohttp_jinja2
from aiohttp import web
# from aiohttpdemo_polls.middlewares import setup_middlewares
from registry_app.routes import setup_routes
from registry_app.models import setup_models
from registry_app.utils import load_config


def init():
    loop = asyncio.get_event_loop()

    # setup application and extensions
    app = web.Application(loop=loop)

    # load config from yaml file in current dir
    conf = load_config(str(pathlib.Path('.') / 'config' / 'registries.yaml'))
    app['config'] = conf

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('registry_app', 'templates'))

    # # create connection to the database
    # app.on_startup.append(init_pg)
    # # shutdown db connection on exit
    # app.on_cleanup.append(close_pg)
    # setup views and routes
    # setup_middlewares(app)
    setup_routes(app)
    setup_models(app)

    return app


def main():
    # init logging
    logging.basicConfig(level=logging.DEBUG)

    app = init()
    web.run_app(app,
                host=app['config']['host'],
                port=app['config']['port'])


if __name__ == '__main__':
    main()