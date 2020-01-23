# -*- coding: utf-8 -*-

'''Python module for initiating and executing commands via REST API.'''

# pylint: disable=too-many-branches, too-many-statements
# pyling: disable=too-many-return-statements

import ujson as json

import requests

from constants import CREDS
from constants import API
from logger import CustomLogger


LOG = CustomLogger(__name__)


class REST(object):
    '''Rest class for invoking REST calls GET, POST, PUT, PATCH, DELETE.'''

    def __init__(self, **kwargs):
        '''This class defines methods to invoke REST calls.

        Args:
            :pcIP (str): IP address.
            :username (str, optional): Username for auth. Default: 'admin'.
            :password (str, optional): Passwd for auth. Default: 'Password'.
            :port (int, optional): Port for sending REST calls. Default: 80.
            :baseURL (str, optional): URI for REST calls. Default: .

        Returns:
            Returns REST object instance.

        Raises: NA
        '''

        self.username = kwargs.pop('username', CREDS.USERNAME)
        self.password = kwargs.pop('password', CREDS.DEFAULT_PASSWORD)
        self.port = kwargs.pop('port', CREDS.PORT)
        self.ip = kwargs.pop('pcIP', CREDS.IP)
        if not self.ip:
            raise NameError('IP address {} not set'.format(self.ip))

        # Disable HTTPS certificate warning.
        requests.packages.urllib3.disable_warnings()

    def post(self, relative_url, **kwargs):
        '''This routine is used to invoke POST call for REST API.

        Args:
            :relative_url(str): Relative URL for the particular API call.
            :kwargs headers(str, optional): Custom headers for REST call.
            :kwargs payload (str, optional): payload to be send for REST call.

        Returns:
            str: response text.
        '''

        kwargs['operation'] = 'post'
        return self.__performOperation(relative_url, **kwargs)

    def get(self, relative_url, **kwargs):
        '''This routine is used to invoke GET call for REST API.

        Args:
            :relative_url(str): Relative URL for the particular API call.
            :kwargs headers(str, optional): Custom headers for REST call.
            :kwargs payload (str, optional): payload to be send for REST call.

        Returns:
            str: response text.
        '''

        kwargs['operation'] = 'get'
        return self.__performOperation(relative_url, **kwargs)

    def patch(self, relative_url, **kwargs):
        '''This routine is used to invoke PATCH call for REST API.

        Args:
            :relative_url(str): Relative URL for the particular API call.
            :kwargs headers(str, optional): Custom headers for REST call.
            :kwargs payload (str, optional): payload to be send for REST call.

        Returns:
            str: response text.
        '''

        kwargs['operation'] = 'patch'
        return self.__performOperation(relative_url, **kwargs)

    def put(self, relative_url, **kwargs):
        '''This routine is used to invoke PUT call for REST API.

        Args:
            :relative_url(str): Relative URL for the particular API call.
            :kwargs headers(str, optional): Custom headers for REST call.
            :kwargs payload (str, optional): payload to be send for REST call.

        Returns:
            str: response text.
        '''

        kwargs['operation'] = 'put'
        return self.__performOperation(relative_url, **kwargs)

    def delete(self, relative_url, **kwargs):
        '''This routine is used to invoke DELETE call for REST API.

        Args:
            :relative_url (str): Relative URL for the particular API call.
            :kwargs headers (str, optional): Custom headers for REST call.
            :kwargs payload (str, optional): payload to be send for REST call.

        Returns:
            str: response text.
        '''

        kwargs['operation'] = 'delete'
        return self.__performOperation(relative_url, **kwargs)

    def __performOperation(self, relative_url, **kwargs):
        '''
        Private Method to perform ops post, get, patch, delete and put.

        Args:
            :relative_url (str): Relative url

        Returns:
          str: Response text.

        Raises: Exception
        '''

        apiVersion = kwargs.pop('apiVersion', API.DEFAULT)
        if apiVersion not in API.VERSION_URL_MAP.keys():
            raise ValueError('apiVersion {} is invalid'.format(apiVersion))

        URL = API.VERSION_URL_MAP.get(apiVersion)
        self.baseURL = 'https://{0}:{1}{2}'.format(
            self.ip, self.port, URL
        )

        mainURI = '{0}{1}'.format(self.baseURL, relative_url)
        headers = kwargs.pop('headers', {'content-type': 'application/json'})
        verify = kwargs.pop('verify', False)
        payload = kwargs.pop('payload', {})
        payload = json.dumps(payload, indent=4) if payload else {}
        auth = (self.username, self.password)
        timeout = kwargs.pop('timeout', 480)
        stream = kwargs.pop('stream', False)
        params = kwargs.pop('params', {})
        operation = kwargs.pop('operation')
        methodToCall = getattr(requests, operation)

        LOG.url('[{0}]: {1}'.format(LOG.yellow(operation.upper()), mainURI))

        if payload:
            LOG.payload("{}".format(payload))

        response = methodToCall(
            mainURI, headers=headers, verify=verify, data=payload,
            auth=auth, timeout=timeout, stream=stream, params=params
        )

        LOG.status(response.status_code)

        # raise exception on failure
        response.raise_for_status()

        if response.status_code != 204 and not stream:
            LOG.response(json.dumps(json.loads(response.content), indent=4))

        if stream:
            return response

        elif response.text is not u'':
            return response.json()

        else:
            return response.text
