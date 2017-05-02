import logging
from io import BytesIO

from openpyxl import load_workbook
from expiringdict import ExpiringDict

from registry_app.gdrive_reader import XLSXDownloadClient

logger = logging.getLogger(__name__)


class RegistryModel(object):
    ru_fields = {
        "страна": "country",
        "сектор": "sector",
        "Название": "title",
        "Платный или бесплатный": "paid",
        "Официальный/неофициальный": "official",
        "Key contact person Контактное лицо": "contact",
        "Описание/Комментарии": "comments",
        "Link/Cсылка": "link",
    }

    en_fields = {
        "country": "country",
        "sector": "sector",
        "Title": "title",
        "Paid or free": "paid",
        "Official/inofficial": "official",
        "Key contact person Контактное лицо": "contact",
        "Description/Comments": "comments",
        "Link/Cсылка": "link",
    }

    def __init__(self, app):
        self.app = app
        self._cache = ExpiringDict(
            max_len=100,
            max_age_seconds=24 * 60 * 60)

        self._downloader = XLSXDownloadClient(
            self.app["config"]["gdrive_config"],
            app.loop)

    @property
    async def ru(self):
        return await self._localized(self.ru_fields)

    @property
    async def en(self):
        return await self._localized(self.en_fields)

    async def _localized(self, fields):
        raw = await self._get_raw()

        return [
            {
                fields[k]: v for k, v in line.items() if k in fields
            }
            for line in raw
        ]

    async def _get_raw(self):
        cached = self._cache.get("_get_raw")
        if cached is not None:
            return cached

        xlsx = await self._downloader.download(
            self.app["config"]["gdrive_spreadsheet_id"])

        resp = []
        wb = load_workbook(BytesIO(xlsx), read_only=True)
        ws = wb.worksheets[1]
        header = []

        def get_row_values(r):
            return [
                c.value for c in r
            ]

        for i, row in enumerate(ws.rows):
            if i == 0:
                header = get_row_values(row)
            else:
                row = get_row_values(row)
                if not any(row):
                    continue

                resp.append(dict(zip(header, row)))

        self._cache["_get_raw"] = resp
        return resp


def setup_models(app):
    app["model"] = RegistryModel(app)
