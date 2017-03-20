import aiohttp_jinja2
from aiohttp import web


@aiohttp_jinja2.template('index.html')
async def index(request):
    registries = await request.app["model"].en

    return {
        "registries": registries
    }

@aiohttp_jinja2.template('whitelabel.html')
async def whitelabel(request):
    registries = await request.app["model"].en

    return {
        "registries": registries
    }

async def api(request):
    registries = await request.app["model"].en

    return web.json_response(
        {
            "registries": registries
        }
    )
