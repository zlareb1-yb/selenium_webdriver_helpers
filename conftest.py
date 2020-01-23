# -*- coding: utf-8 -*-

# pylint: disable=bare-except, global-variable-undefined, invalid-name
# pylint: disable=redefined-builtin, redefined-outer-name
# pylint: disable=dangerous-default-value


'''conftest for UI testcases'''
import logging
import re

import pytest
import sys
import os
import uuid
import json

#from pytest_reportportal import RPLogger, RPLogHandler

from logger import CustomLogger
from webdriver import Selenium
from constants import CREDS
from rest import REST

LOG = CustomLogger(__name__)
selenium = None

@pytest.fixture(scope='session', autouse=True)
def start_browser_and_login_as_admin():
    global selenium
    selenium = Selenium()
    yield
    try:
        LOG.info("executing yield")
        LOG.info("current url: {}".format(selenium.driver.current_url))
        if os.getenv("COVERAGE") is not None:
            LOG.info("***********  Coverage   **************")
            dir_path = os.path.dirname(os.path.realpath(__file__))
            coverage_dir = os.path.join(dir_path, "coverage")
            if not os.path.exists(coverage_dir):
                os.mkdir(coverage_dir)
            js = selenium.driver.execute_script('return window.__coverage__;')
            file_name = str(uuid.uuid1())[:5] + "_cov.json"
            LOG.info("Coverage Report File - {}".format(file_name))
            with open(os.path.join(coverage_dir, file_name), 'w') as outfile:
                json.dump(js, outfile)
        selenium.driver.quit()
        selenium.display.stop()
    except Exception:
        pass

"""
@pytest.fixture(scope="session", autouse=True)
def rp_logger(request):
    '''
    This routine is to create reportportal handler.
    Args:
        request(object): pytest test object
    Returns:
        logger (object) : logger object
    '''
    logging.setLoggerClass(RPLogger)
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if hasattr(request.node.config, 'py_test_service'):
        rp_handler = RPLogHandler(request.node.config.py_test_service)
    else:
        rp_handler = logging.StreamHandler(sys.stdout)

    rp_handler.setLevel(logging.INFO)
    pytest.rp_logger = logger
    global LOG
    LOG = logger
    return logger
"""

@pytest.fixture(scope='function', autouse=True)
def get_into_app_for_test_method():
    load_apps_page()


@pytest.fixture(scope='class', autouse=True)
def get_into_application_page_for_test_class():
    load_apps_page()


def load_apps_page():
    '''
    This routine loads /apps page before testcase begins
    '''
    LOG.debug("running load /apps page fixture")
    #selenium = Selenium()
    current_url = selenium.driver.current_url
    pattern = '.*[0-9]/apps/$'

    LOG.info("current url: {}".format(current_url))
    if bool(re.match(pattern, current_url)):
        LOG.info("page already in /apps page")
    elif 'login' in current_url:
        selenium.login()
    else:
        selenium.load_application_page()

@pytest.fixture(scope='class')
def rest():
    """
    calls rest.py and returns rest object
    Returns:
        REST (object) : Rest object instance.
    """
    kwargs = {}
    kwargs['username'] = CREDS.USERNAME
    kwargs['password'] = CREDS.DEFAULT_PASSWORD
    kwargs['ip'] = CREDS.IP
    port = CREDS.PORT

    kwargs['base_uri'] = 'https://{0}:{1}/api/v3/'.format(
        kwargs['ip'], port
    )
    return REST(**kwargs)
