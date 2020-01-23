# -*- coding: utf-8 -*-
'''constants'''

# pylint: disable=missing-docstring, invalid-name, line-too-long


import uuid
import os

from utils import get_script_folder_path


class CREDS:
    IP = ''
    PORT = 80
    URL = 'https://{0}:{1}'.format(IP, PORT)
    USERNAME = 'admin'
    DEFAULT_PASSWORD = 'Password'

class API:
    VERSION = '3.0'
    DEFAULT = 'v3'
    VERSION_URL_MAP = {
        'v3': '/api/v3'
    }

class UI_SCROLL_POSITIONING:
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    TOP_CENTER = "top_center"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"
