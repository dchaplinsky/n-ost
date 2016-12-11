import aiohttp_jinja2
from aiohttp import web


@aiohttp_jinja2.template('index.html')
async def index(request):
    resp = await request.app["model"].uk

    return {
        "size": len(resp),
        "resp": resp
    }
