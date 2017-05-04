import aiohttp_jinja2
from aiohttp import web


def get_lang(req, default="en"):
    lang = req.GET.get("lang", default).lower()
    if lang in ("ru", "en"):
        return lang

    return default


@aiohttp_jinja2.template('index.html')
async def index(request):
    lang = get_lang(request)

    registries = await getattr(request.app["model"], lang)

    return {
        "registries": registries,
        "lang": lang
    }


@aiohttp_jinja2.template('whitelabel.html')
async def whitelabel(request):
    lang = get_lang(request)
    set_default_locale(lang)

    registries = await getattr(request.app["model"], lang)

    return {
        "registries": registries,
        "lang": lang
    }


async def api(request):
    lang = get_lang(request)
    registries = await getattr(request.app["model"], lang)

    return web.json_response(
        {
            "registries": registries
        }
    )
