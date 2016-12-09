import aiohttp
import datetime
import httplib2
import logging
import json
from oauth2client.client import HttpAccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials


logger = logging.getLogger(__name__)
_UTCNOW = datetime.datetime.utcnow


# Async version of ServiceAccountCredentials
class AIOHTTPServiceAccountCredentials(ServiceAccountCredentials):
    async def refresh(self, http):
        """Forces a refresh of the access_token.

        Args:
            http: httplib2.Http, an http object to be used to make the refresh
                  request.
        """
        await self._refresh(http)

    async def _refresh(self, http):
        """Refreshes the access_token.

        This method first checks by reading the Storage object if available.
        If a refresh is still needed, it holds the Storage lock until the
        refresh is completed.

        Args:
            http: an object to be used to make HTTP requests.

        Raises:
            HttpAccessTokenRefreshError: When the refresh fails.
        """
        if not self.store:
            await self._do_refresh_request(http)
        else:
            self.store.acquire_lock()
            try:
                new_cred = self.store.locked_get()

                if (new_cred and not new_cred.invalid and
                        new_cred.access_token != self.access_token and
                        not new_cred.access_token_expired):
                    logger.info('Updated access_token read from Storage')
                    self._updateFromCredential(new_cred)
                else:
                    await self._do_refresh_request(http)
            finally:
                self.store.release_lock()

    async def _do_refresh_request(self, http):
        """Refresh the access_token using the refresh_token.

        Args:
            http: an object to be used to make HTTP requests.

        Raises:
            HttpAccessTokenRefreshError: When the refresh fails.
        """
        body = self._generate_refresh_request_body()
        headers = self._generate_refresh_request_headers()

        logger.info('Refreshing access_token')

        async with http.post(
                self.token_uri, data=body, headers=headers) as resp:
            content = await resp.text()

            if resp.status == 200:
                d = json.loads(content)
                self.token_response = d
                self.access_token = d['access_token']
                self.refresh_token = d.get('refresh_token', self.refresh_token)
                if 'expires_in' in d:
                    delta = datetime.timedelta(seconds=int(d['expires_in']))
                    self.token_expiry = delta + _UTCNOW()
                else:
                    self.token_expiry = None
                if 'id_token' in d:
                    self.id_token = _extract_id_token(d['id_token'])
                else:
                    self.id_token = None
                # On temporary refresh errors, the user does not actually have to
                # re-authorize, so we unflag here.
                self.invalid = False
                if self.store:
                    self.store.locked_put(self)
            else:
                # An {'error':...} response body means the token is expired or
                # revoked, so we flag the credentials as such.
                logger.info('Failed to retrieve access token: %s', content)
                error_msg = 'Invalid response {0}.'.format(resp.status)
                try:
                    d = json.loads(content)
                    if 'error' in d:
                        error_msg = d['error']
                        if 'error_description' in d:
                            error_msg += ': ' + d['error_description']
                        self.invalid = True
                        if self.store is not None:
                            self.store.locked_put(self)
                except (TypeError, ValueError):
                    pass
                raise HttpAccessTokenRefreshError(error_msg, status=resp.status)


class XLSXDownloadClient(object):
    """
    Class to quickly export google spreadsheet into XLSX and download it.

    Currently not in use
    """

    def __init__(self, credentials_file, loop):
        self.credentials_file = credentials_file
        self.loop = loop
        super(XLSXDownloadClient, self).__init__()

    async def get_auth_token(self, session):
        SCOPES = ['https://spreadsheets.google.com/feeds']
        credentials = AIOHTTPServiceAccountCredentials.from_json_keyfile_name(
            self.credentials_file, SCOPES)

        await credentials.refresh(session)
        return credentials.token_response["access_token"]

    async def download(self, spreadsheet, format="xlsx"):
        url = ("https://spreadsheets.google.com/feeds/download/"
               "spreadsheets/Export?key=%s&exportFormat=%s" % (spreadsheet, format))

        with aiohttp.ClientSession(loop=self.loop) as session:
            headers = {
                "Authorization": "Bearer " + (await self.get_auth_token(session))
            }

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    raise Exception()
