from io import BytesIO
import pathlib
from openpyxl import load_workbook

from registry_app.gdrive_reader import XLSXDownloadClient


PROJECT_ROOT = pathlib.Path(__file__).parent


class RegistryModel(object):
    def __init__(self, app):
        self.app = app
        self._downloader = XLSXDownloadClient(
            self.app["config"]["gdrive_config"],
            app.loop)

    @property
    async def uk(self):
        raw = await self._get_raw()
        return raw

    @property
    async def en(self):
        raw = await self._get_raw()
        return raw

    async def _get_raw(self):
        xlsx = await self._downloader.download(
            self.app["config"]["gdrive_spreadsheet_id"])

        wb = load_workbook(BytesIO(xlsx), read_only=True)
        for ws in wb.worksheets:
            for row in ws.rows:
                pass


def setup_models(app):
    app["model"] = RegistryModel(app)
