import os
import json
import asyncio
import logging
import pathlib

import jinja2

from aiohttp import web

import aiohttp_jinja2
from registry_app.middlewares import setup_middlewares
from registry_app.routes import setup_routes
from registry_app.models import setup_models
from registry_app.utils import load_config


def init():
    loop = asyncio.get_event_loop()

    # setup application and extensions
    app = web.Application(loop=loop)

    app['config'] = {
        "gdrive_config": json.loads(os.getenv("gdrive_config", "{}")),
        "gdrive_spreadsheet_id": os.getenv("gdrive_spreadsheet_id", "")
    }

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('registry_app', 'templates'),
    )

    setup_middlewares(app)
    setup_routes(app)
    setup_models(app)

    return app
