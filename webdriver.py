# -*- coding: utf-8 -*-
'''Helper for Clicking WebElement'''

# pylint: disable=broad-except

import os
import time

from pyvirtualdisplay import Display as PyVTDisplay
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, \
    StaleElementReferenceException, InvalidElementStateException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import constants
from logger import CustomLogger
from singleton import Singleton
from utils import retries, set_locator, get_script_folder_path
import webdriver as WD_PF


LOG = CustomLogger(__name__)


class BaseDriver(metaclass=Singleton):
    '''base driver class to initialize web driver'''

    def __init__(self):
        '''
        constructor for driver class
        Args:
            :None:
        '''
        self.driver = None
        self.display = None
        self.AC = None
        self.setup_driver()

    def setup_driver(self):
        LOG.info('setting up webdriver and starting browser')
        try:
            self.display = PyVTDisplay(visible=0, size=(1680, 1050))
            self.display.start()
        except Exception:
            pass

        if os.environ["browser"] == "chrome":
            chrome_options = ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument("--start-fullscreen")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("disable-infobars")
            chrome_options.add_argument("enable-automation")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")

            # Adding download preferences for chrome
            script_dir = get_script_folder_path()
            preferences = {
                "download.default_directory": script_dir,
                "directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", preferences)
            self.driver = webdriver.Chrome(
                os.getenv("CHROME_PATH"), options=chrome_options
            )

            # self.driver = webdriver.Remote('http://localhost:32769/wd/hub', chrome_options.to_capabilities())

            self.AC = ActionChains(self.driver)
            # self.driver.set_window_size(1680, 1050)
            # add missing support for chrome "send_command"
            # to selenium webdriver
            self.driver.command_executor._commands["send_command"] = \
                ("POST", '/session/$sessionId/chromium/send_command')

            params = {
                'cmd': 'Page.setDownloadBehavior',
                'params': {
                    'behavior': 'allow',
                    'downloadPath': script_dir
                }
            }
            self.driver.execute("send_command", params)
        else:
            fp = webdriver.FirefoxProfile()
            fp.set_preference("dom.max_chrome_script_run_time", 60)
            fp.set_preference("dom.max_script_run_time", 60)
            self.driver = webdriver.Firefox(firefox_profile=fp)
            self.driver.fullscreen_window()

        self.get_into_login_page()
        LOG.info('driver setup complete and browser is instantiated')

    def get_into_login_page(self):
        url = self.get_url()
        LOG.info("loading url: {}".format(url))
        self.driver.get(url)
        self.driver.set_page_load_timeout(50)
        self.driver.implicitly_wait(10)
        self.driver.set_script_timeout(10)

    def get_url(self):
        return ('https://%s:%s' % (
            constants.CREDS.IP, constants.CREDS.PORT
        ))


class Wait(BaseDriver):
    '''base wait class that implments selenium wait methods'''

    def wait_until_element_present(self, element, timeout=300):
        '''
        Waits until element is present
        Args:
            element (tuple): Element locator
            timeout (int): timeout in seconds
        '''

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(element)
            )

        except TimeoutException:
            LOG.error('failed to find element %s' % element[1])
            raise NoSuchElementException

        except Exception:
            raise

    def wait_until_element_not_present(self, element, timeout=300):
        '''
        Waits until element is not present
        Args:
            element (tuple): Element locator
            timeout (int): timeout in seconds
        '''
        try:
            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located(element)
            )

        except Exception:
            LOG.error("element %s is present" % element[1])
            raise

    def wait_until_page_loads(self, page_start, timeout=300):
        '''
        Waits until page is loaded
        Args:
            element (tuple): Element locator
            page_start (string): Page start string
            timeout (int): timeout in seconds
        '''

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.title.lower().startswith(page_start)
            )

        except Exception:
            LOG.error('failed to load page %s' % page_start)
            raise

    def wait_until_element_visible(self, element, timeout=300):
        '''
        Waits until element is visible in timeout secs
        Args:
            element (tuple): Element locator
            timeout (int): timeout in seconds
        Raises:
            NoSuchElementException on failure
        '''

        LOG.info("waiting for '%s' element to be visible: %s" % (element[1], timeout))

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(element)
            )

        except TimeoutException:
            LOG.error('element invisible: %s' % element[1])
            raise NoSuchElementException

        except Exception:
            raise

    def wait_until_element_not_visible(self, element, timeout=300):
        '''
        Waits until element is not visible in timeout secs
        Args:
            element (tuple): Element locator
            timeout (int): timeout in seconds
        Raises:
            Exception
        '''

        LOG.info("waiting for '%s' element to be invisible: %s" % (element[1], timeout))

        try:
            WebDriverWait(self.driver, timeout).until_not(
                EC.visibility_of_element_located(element)
            )

        except Exception:
            LOG.error('element visible: %s' % element[1])
            raise

    def wait_until_element_is_clickable(self, element, timeout=300):
        '''
        Waits until element becomes clickable until timeout secs
        Args:
            element (tuple): Element locator
            timeout (int): timeout in seconds
        Raises:
            NoSuchElementException
        '''

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element)
            )

        except TimeoutException:
            LOG.warning('element %s is not clickable' % element[1])
            raise TimeoutException

        except Exception:
            raise

    def wait_for_text(self, element, text, timeout=300):
        '''
        Waits until text to be present in the element
        Args:
            element (tuple): Element locator
            text (string): Text to be present
            timeout (int): timeout in seconds
        Raises:
            NoSuchElementException
        '''

        try:
            WebDriverWait(self.driver, timeout).until(
                EC.text_to_be_present_in_element(element, text)
            )

        except TimeoutException:
            LOG.error('failed to find element %s' % element[1])
            raise NoSuchElementException

        except Exception:
            raise


class Browser(Wait):
    '''base browser class that implments selenium browser methods'''

    def is_element_present(self, locator):
        '''
        method to return True if locator element is present on UI else False.
        Args:
            locator(tuple): Web element locator
        Returns:
             boolean: True if element is present on UI else False.
        '''

        try:
            self.driver.find_element(*locator)

        except Exception:
            return False

        return True

    def is_element_absent(self, locator):
        '''
        Returns boolean depending on element param <locator> presence
        Args:
            locator(tuple): Web element locator
        Returns:
            boolean
        '''

        try:
            self.driver.find_element(*locator)

        except Exception:
            return True

        return False

    def is_visible(self, element, timeout=1):
        '''
        Return True if element is visible within 2 seconds, otherwise False
        Args:
            element (tuple): Element locator
            timeout (int) : Timeout secs for webdriver wait
        Returns:
            boolean
        '''

        try:
            self.wait_until_element_visible(element, timeout)
            return True

        except TimeoutException:
            return False

        except NoSuchElementException:
            return False

    def is_not_visible(self, element, timeout=1):
        '''
        Return True or False if element is not visible within 2 seconds
        Args:
            element (tuple): Element locator
            timeout (int) : Timeout secs for webdriver wait
        Returns:
            boolean
        '''

        try:
            self.wait_until_element_not_visible(element, timeout)
            return True

        except TimeoutException:
            return False

    def is_element_clickable(self, element, timeout=2):
        '''
        Return True or False if element is not clickable within 2 seconds
        Args:
            element (tuple): Element locator
            timeout (int) : Timeout secs for webdriver wait
        Returns:
            boolean
        '''
        try:
            self.wait_until_element_is_clickable(element, timeout)
            return True

        except TimeoutException:
            return False

        except NoSuchElementException:
            return False

    def get_current_url(self):
        '''
        This routine returns current url of the browser
        Returns:
            str : Current url of the browser
        '''

        return self.driver.current_url

    def is_element_disabled(self, locator):
        '''
        This routine checks if the given element is disabled or not
        Args:
            locator(tuple) : WebElement locator
        Returns:
            (bool) True if element is disabled else false
        '''

        element = self.driver.find_element(*locator)
        return element.get_attribute('disabled') is not None

    # To be only be called from library, do not include in any web driver functions
    def scroll_middle(self, locator):
        '''
                This routine scrolls the view to the <element>.
                Args:
                    element(tuple): web element locator to which you want to scroll
                '''

        element = self.driver.find_element(*locator)

        scroll_middle = "var viewPortHeight = Math.max(" \
                        "document.documentElement.clientHeight, window.innerHeight " \
                        "|| 0); var elementTop = arguments[0].getBoundingClientRect().top;" \
                        "window.scrollBy(0, elementTop-(viewPortHeight/2));"

        self.driver.execute_script(scroll_middle, element)

    def bring_element_into_focus(self, element, scrollbar_identifier=None,
                                 position=constants.UI_SCROLL_POSITIONING.TOP_LEFT):
        """
        This routine brings the given element into focus by moving to the
        region of the bounded rectangle of the element.

        Args:
            element(tuple): web element locator which you want to locate and
                            focus.
            scrollbar_identifier(tuple): if the element is bounded within a
                                         nested scrollbar, this gives the web
                                         element locator of the scrollbar.
            position(str): position within the bounded rectangle to which you
                           want to scroll.

        Returns:
            None
        """
        target_element = self.driver.find_element(*element)
        bounding_rectangle = self.driver.execute_script( \
            "return arguments[0].getBoundingClientRect();", target_element)
        LOG.info("Coordinates of element: %s" % (bounding_rectangle))

        top_coord = bounding_rectangle["top"]
        left_coord = bounding_rectangle["left"]
        height = bounding_rectangle["height"]
        width = bounding_rectangle["width"]

        x_coord = None
        y_coord = None

        if position == constants.UI_SCROLL_POSITIONING.TOP_LEFT:
            x_coord = left_coord
            y_coord = top_coord
        elif position == constants.UI_SCROLL_POSITIONING.TOP_CENTER:
            x_coord = left_coord + width/2
            y_coord = top_coord
        elif position == constants.UI_SCROLL_POSITIONING.TOP_RIGHT:
            x_coord = left_coord + width
            y_coord = top_coord
        elif position == constants.UI_SCROLL_POSITIONING.BOTTOM_LEFT:
            x_coord = left_coord
            y_coord = top_coord + height
        elif position == constants.UI_SCROLL_POSITIONING.BOTTOM_CENTER:
            x_coord = left_coord + width/2
            y_coord = top_coord + height
        elif position == constants.UI_SCROLL_POSITIONING.BOTTOM_RIGHT:
            x_coord = left_coord + width
            y_coord = top_coord + height

        x_coord = int(x_coord)
        y_coord = int(y_coord)

        if scrollbar_identifier:
            scrollbar_element = self.driver.find_element(*scrollbar_identifier)
            self.driver.execute_script("arguments[0].scrollTo(%d, %d);" %
                                       (x_coord, y_coord), scrollbar_element)
        else:
            self.driver.execute_script("window.scrollTo(%d, %d);" %
                                       (x_coord, y_coord))

        self.driver.execute_script("arguments[0].focus();", target_element)

    def scroll_into_view(self, element):
        '''
        This routine scrolls the view to the <element>.
        Args:
            element(tuple): web element locator to which you want to scroll
        '''
        element = self.driver.find_element(*element)
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

    def scroll_from_top(self, element, timeout=10):
        '''
        scroll the view to the <element> by searching it from top
        Args:
            element (tuple): web element locator to which you want to scroll
            timeout (int) : Timeout value for a wait
        Raises:
            NoSuchElementException
        '''

        self.driver.execute_script(
            "window.scrollTo(document.body.scrollHeight, 0);"
        )

        timeout += time.time()
        while not self.is_visible(element, timeout=1):
            self.driver.execute_script("window.scrollBy(0, 250)")
            if time.time() > timeout:
                LOG.error("failed to find element {}".format(element[1]))
                raise NoSuchElementException

    def take_screenshot(self, test_name="test"):
        '''
        Take screenshot of the browser
        Args:
            test_name (str): Name of the test
        '''

        path = '{0}/ui/screenshots/{1}.png'.format(
            os.path.dirname(os.getcwd()), test_name
        )

        self.driver.get_screenshot_as_file(path)
        LOG.info("screenshot of failed test case saved at %s" % path)


class Label(Browser):
    '''base click class that implments selenium label methods'''

    def get_text(self, locator, timeout=180):
        '''
        This routine returns text from the label
        Args:
            locator (tuple):  locator and locator type
            timeout (int): timeout in seconds
        Returns:
            str: text of the web element.
        '''

        try:
            self.wait_until_element_present(locator, timeout)
            self.scroll_into_view(locator)
            element = self.driver.find_element(*locator)
            self.driver.execute_script(
                "arguments[0].scrollIntoView();", element
            )

            return element.text

        except TimeoutException:
            LOG.error("failed to find element {}".format(locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def get_attribute(
            self, attribute, locator, is_multiple_attributes=False, timeout=180
    ):
        '''This routine gets particular attribute's value of an web element
        Args:
            attribute (str): Name of the attribute
            locator (tuple): Locator of the web element
            is_multiple_attributes (boolean): True for multiple attributes
            timeout (int): timeout in seconds
        Returns:
            str: value of the param <attribute> of the param <locator>
        '''

        try:
            self.wait_until_element_present(locator, timeout)
            if is_multiple_attributes:
                attributes = []
                elements = self.driver.find_elements(*locator)
                for element in elements:
                    attributes.append(element.get_attribute(attribute))
                return attributes
            else:
                if not self.is_visible(locator):
                    self.scroll_into_view(locator)
                element = self.driver.find_element(*locator)
                return element.get_attribute(attribute)

        except TimeoutException:
            LOG.error("failed to find element {}".format(locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def get_property(
            self, property, locator, is_multiple_properties=False, timeout=180
    ):
        '''This routine gets particular property's value of an web element
        Args:
            property (str): Name of the property
            locator (tuple): Locator of the web element
            is_multiple_properties (boolean): True for multiple properties
            timeout (int): timeout in seconds
        Returns:
            str: value of the param <attribute> of the param <locator>
        '''

        try:
            self.wait_until_element_present(locator, timeout)
            self.scroll_into_view(locator)
            if is_multiple_properties:
                attributes = []
                elements = self.driver.find_elements(*locator)
                for element in elements:
                    attributes.append(element.get_property(property))
                return attributes
            else:
                element = self.driver.find_element(*locator)
                return element.get_property(property)

        except TimeoutException:
            LOG.error("failed to find element {}".format(locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

class Click(Label):
    '''base click class that implments selenium click methods'''
    def button(self, locator, timeout=180):
        '''
        Clicks on a button
        Args:
            locator (webelement): Web element to click.
            timeout (int): timeout in seconds
        Raises:
            NoSuchElementException
        Returns: None
        '''

        try:
            element = None
            element = self.driver.find_element(*locator)
            self.AC.reset_actions()
            self.AC.move_to_element(element).perform()
            self.wait_until_element_is_clickable(locator, timeout)
            self.click_after_confirm(locator)

        except TimeoutException:
            LOG.error("failed to find element {}".format(locator[1]))
            raise NoSuchElementException

        except Exception:
            try:
                self.scroll_from_top(locator, timeout=60)
                self.click_after_confirm(locator)
            except Exception:
                try:
                    self.scroll_into_view(locator)
                    self.click_after_confirm(locator)
                except Exception:
                    if element is not None:
                        LOG.info("Javascript Button Click on {}".format(element))
                        try:
                            self.driver.execute_script(
                                "arguments[0].click();", element
                            )
                        except Exception as exception:
                            LOG.info(exception)
                            raise
                    else:
                        raise

    def click_after_confirm(self, locator, timeout=60,
                            ignored_exceptions=(NoSuchElementException,
                                                StaleElementReferenceException)):
        '''

            This will poll an element, ignoring exceptions
            in the provided iterable for the specified period.

            Args:
                locator (webelement): Web element to click.
                timeout (int): timeout in seconds
                ignored_exceptions (iterable): iterable structure of exception classes ignored during calls
            Raises:
                NoSuchElementException
            Returns: None
        '''

        try:
            ignored_exceptions = ignored_exceptions
            element = WebDriverWait(self.driver, timeout=timeout,
                                    ignored_exceptions=ignored_exceptions) \
                .until(EC.presence_of_element_located(locator))
            element.click()
        except Exception as exception:
                    LOG.info(exception)
                    raise

    def wait_for_availibility(self, locator, timeout=180,
                            ignored_exceptions=(NoSuchElementException,
                                                StaleElementReferenceException, InvalidElementStateException)):

        '''

        This will poll an element, ignoring exceptions
        in the provided iterable for the specified period.

        Args:
            locator (webelement): Web element to check.
            timeout (int): timeout in seconds
            ignored_exceptions (iterable): iterable structure of exception classes ignored during calls
        Raises:
            NoSuchElementException
        Returns: WebElement
        '''

        try:
            ignored_exceptions = ignored_exceptions
            element = WebDriverWait(self.driver, timeout=timeout,
                                    ignored_exceptions=ignored_exceptions) \
                .until(EC.presence_of_element_located(locator))

            return element

        except Exception:
            raise

    def hoverclick(self, movetoelement, locator, timeout=180):
        '''
        Hovers a button and Clicks on it.

        Args:
            movetoelement(webelement): Webelement to Hover upon.
            locator (webelement): Webelement to click.
            timeout (int): timeout in seconds

        Raises:
            ElementNotFound, ElementNotClickable

        Returns: None
        '''

        try:
            self.wait_until_element_present(movetoelement, timeout)
            element = self.driver.find_element(*movetoelement)
            element1 = self.driver.find_element(*locator)
            self.AC.reset_actions()
            self.AC.move_to_element(element).click(element1).perform()

        except Exception:
            raise

    def toggle_checkbox(self, locator, desired_state):
        '''
        This routine toggles state based on current state and desired state

        Args:
             locator (Tuple): locator of the checkbox
             desired_state (Boolean): toggles to desired state
        '''

        current_state = self.get_attribute("value", locator) == "true"
        if current_state != desired_state:
            LOG.info("changing state - {0} with value - {1}".format(
                locator, desired_state
            ))
            self.scroll_from_top(locator)
            self.button(locator)

    def toggle_runtime(self, locator, desired_state):
        '''
        This routine toggles state based on current state and desired state
        Args:
             locator (Tuple): locator of the runtime button
             desired_state (Boolean): toggles to desired state
        '''

        current_state = self.get_attribute("class", locator)
        self.scroll_from_top(locator)
        if "active" in current_state and not desired_state:
            self.button(locator)
        # If the runtime locator has a class with "inactive" appended to it,
        # click on the button.
        elif "inactive" in current_state and desired_state:
            self.button(locator)
        elif "active" not in current_state and desired_state:
            self.button(locator)


class Input(Click):
    '''base input class that implments selenium input methods'''

    def textbox(self, value, locator, clear=True, timeout=180):
        '''
        This routine is used to place content in an input box.
        Args:
            value (any) : The value that you want to place in input box.
            locator (tuple): locator of the input box.
            clear (boolean): Set to True to clear the input box
            timeout (int): timeout in seconds
        '''

        try:
            self.wait_until_element_present(locator, timeout)
            self.scroll_into_view(locator)
            element = self.driver.find_element(*locator)
            if clear:
                element.clear()

                # If there is driver mismatch use the below to clear in local
                for _ in range(len(element.get_attribute('value'))):
                    element.send_keys(Keys.BACK_SPACE)

            element.send_keys(value)
            time.sleep(1)

        except TimeoutException:
            LOG.error("failed to find element {}".format(locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def fileinput(self, file_path, locator, timeout=180):
        '''
        This routine is used to perform fiel upload action from local
        Args :
            file_path (str) : location of file to be uploaded
            locator (list) : locator of upload button
            timeout (int): timeout in seconds
        '''
        try:
            self.wait_until_element_present(locator, timeout)
            self.scroll_into_view(locator)
            element = self.driver.find_element(*locator)
            element.send_keys(file_path)
            time.sleep(1)

        except TimeoutException:
            LOG.error("failed to find element {}".format(locator[1]))
            raise NoSuchElementException

        except Exception:
            raise


class Dropdown(Input):
    '''base dropdown class that implments selenium dropdown methods'''

    def select(
            self,
            drop_down_label,
            value_to_select,
            index=1,
            is_clear_existing_value=False,
            is_clear_all=False,
            timeout=180
    ):
        '''
        This routines enable to select an option from the dropdown.
        Args:
            drop_down_label (str): Label of the dropdown
            value_to_select (any):  Value to select from the dropdown
            index (int):  index th drop down (with same label) from the page.
            is_clear_existing_value (bool): To clear existing values
            timeout (int): timeout in seconds
        '''

        try:
            label_locator = set_locator(
                WD_PF.DROPDOWN.LABEL_XPATH,
                (drop_down_label, str(index))
            )

            negative_case = False
            if not value_to_select:
                negative_case = True
            if is_clear_existing_value or negative_case:
                if is_clear_all:
                    clear_locator = set_locator(
                        WD_PF.DROPDOWN.CLEAR_ALL_XPATH,
                        (drop_down_label, str(index))
                    )
                else:
                    clear_locator = set_locator(
                        WD_PF.DROPDOWN.CLEAR_VALUE_XPATH,
                        (drop_down_label, str(index))
                    )
                if negative_case:
                    if drop_down_label not in self.get_text(label_locator):
                        self.button(clear_locator)
                    return
                self.button(clear_locator)

            self.wait_until_element_present(label_locator, timeout)
            self.scroll_into_view(label_locator)
            self.wait_until_element_is_clickable(label_locator, timeout)
            if self.is_element_absent(label_locator):
                self.scroll_into_view(label_locator)
            time.sleep(1)
            self.button(label_locator)

            value_locator = set_locator(
                WD_PF.DROPDOWN.SELECT_VALUE_XPATH, value_to_select
            )

            if self.is_element_absent(value_locator):
                self.scroll_into_view(value_locator)
            self.button(value_locator)

        except TimeoutException:
            LOG.error("failed to find element {}".format(label_locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def select_by_search(
            self,
            drop_down_label,
            value_to_select,
            index=1,
            is_clear_existing_value=False,
            timeout=180
    ):
        '''
        This routines enable to select an option from the dropdown.
        Args:
            drop_down_label (str): Label of the dropdown
            value_to_select (any):  Value to select from the dropdown
            index (int):  index th drop down (with same label) from the page.
            is_clear_existing_value (bool): To clear existing values
            timeout (int): timeout in seconds
        '''

        try:
            negative_case = False
            if not value_to_select:
                negative_case = True
            if is_clear_existing_value or negative_case:
                clear_locator = set_locator(
                    WD_PF.DROPDOWN.CLEAR_VALUE_XPATH,
                    (drop_down_label, str(index))
                )
                if negative_case:
                    if not self.is_element_absent(clear_locator):
                        self.button(clear_locator)
                    return
                self.button(clear_locator)

            label_locator = set_locator(
                WD_PF.DROPDOWN.SELECT_ARROW_IDX_XPATH,
                (drop_down_label, str(index))
            )

            self.wait_until_element_present(label_locator, timeout)
            self.scroll_into_view(label_locator)
            self.wait_until_element_is_clickable(label_locator, timeout)
            self.scroll_into_view(label_locator)
            time.sleep(1)
            self.button(label_locator)
            self.textbox(value_to_select, set_locator(
                WD_PF.DROPDOWN.SELECT_INPUT_XPATH, drop_down_label
            ))

            value_locator = set_locator(
                WD_PF.DROPDOWN.SELECT_VALUE_XPATH, value_to_select
            )
            self.scroll_into_view(value_locator)
            self.button(value_locator)

        except TimeoutException:
            LOG.error("failed to find element {}".format(label_locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def select_by_label_xpath(self, label_xpath, value_to_select, timeout=180):
        '''
        Enables to select an option from dropdown using label_xpath
        Args:
            label_xpath (tuple) : label xpath by xpath locator
            value_to_select (str) : dropdown value
            timeout (int): timeout in seconds
        '''

        try:
            negative_case = False
            if not value_to_select:
                negative_case = True
            if negative_case:
                clear_xpath = list(label_xpath)
                clear_xpath[1] += WD_PF.DROPDOWN.CLEAR_VALUE
                clear_xpath = tuple(clear_xpath)
                clear_locator = clear_xpath
                dropdown_text = self.get_text(label_xpath)
                if "Select" not in dropdown_text and dropdown_text not in \
                        label_xpath[1]:
                    self.button(clear_locator)
                return
            self.wait_until_element_visible(label_xpath, timeout)
            self.scroll_from_top(label_xpath)
            self.wait_until_element_is_clickable(label_xpath, timeout)

            # This is the fix for the dropdown issue where we need to click on the dropdown arrow if clickable to select
            # the value.
            if isinstance(label_xpath, list):
                label_xpath = tuple(label_xpath)
            dropdown_locator = label_xpath + WD_PF.DROPDOWN.DROPDOWN_ICON
            if self.is_element_present(dropdown_locator) and self.is_element_clickable(dropdown_locator):
                self.button(dropdown_locator)
            else:
                self.button(label_xpath)

            value_locator = set_locator(
                WD_PF.DROPDOWN.SELECT_VALUE_XPATH, value_to_select
            )

            if self.is_element_absent(value_locator):
                self.scroll_into_view(value_locator)
            self.button(value_locator)

        except TimeoutException:
            LOG.error("failed to find element {}".format(label_xpath[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def select_by_label_xpath_with_focus_on_other_element(
            self, label_xpath, value_to_select, other_element, timeout=180
    ):
        '''
        select an option from dropdown using label_xpath and other_element
        Args:
            label_xpath (tuple) : label xpath by xpath locator
            value_to_select (str) : dropdown value
            other_element (tuple) : other element locator to be focused
            timeout (int): timeout in seconds
        '''
        try:
            self.wait_until_element_visible(label_xpath, timeout)
            self.scroll_into_view(other_element)
            self.button(label_xpath)
            self.button(set_locator(
                WD_PF.DROPDOWN.SELECT_VALUE_XPATH, value_to_select
            ))

        except TimeoutException:
            LOG.error("failed to find element {}".format(label_xpath[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def search_and_select(
            self, search_input_box, value_to_select, value_locator
    ):

        '''
        search an option from dropdown box, when dropdown options are many
        Args:
            search_input_box (tuple) : dropdown input xpath
            value_to_select (str) : dropdown value
            value_locator (tuple): dropdown select value xpath
        '''

        try:
            self.textbox(value_to_select, search_input_box)
            self.button(value_locator)

        except TimeoutException:
            LOG.error("failed to find element {}".format(value_locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def get_all_options(self, drop_down_label, timeout=180):
        '''
        This routines returns all the available options from dropdown
        Args:
            drop_down_label (str): Label of the dropdown
            index (int):  index th drop down (with same label) from the page.
            timeout (int): timeout in seconds
        Returns:
            list of available options
        '''
        try:
            label_locator = set_locator(
                WD_PF.DROPDOWN.SELECT_ARROW_XPATH, drop_down_label
            )

            self.wait_until_element_present(label_locator, timeout)
            self.wait_until_element_is_clickable(label_locator, timeout)
            self.scroll_into_view(label_locator)
            time.sleep(1)
            self.button(label_locator)
            options_locator = WD_PF.DROPDOWN.SELECT_OPTIONS_XPATH
            options_text = self.driver.find_element(*options_locator).text
            options_list = options_text.split("\n")
            LOG.info("available options: %s" % options_list)
            return options_list

        except TimeoutException:
            LOG.error("failed to find element {}".format(label_locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def select_by_value_locator(
            self, drop_down_label, value_locator, index=1, timeout=180
    ):
        '''
        This routine allows selection of drop down value by the xpath
        Args:
            drop_down_label (str): Label of the dropdown
            value_locator (obj): locator of the dropdown value
            index (int):  index th drop down (with same label) from the page.
            timeout (int): timeout in seconds
        '''

        try:
            label_locator = set_locator(
                WD_PF.DROPDOWN.LABEL_XPATH,
                (drop_down_label, str(index))
            )

            self.wait_until_element_present(label_locator, timeout)
            self.wait_until_element_is_clickable(label_locator, timeout)
            if self.is_element_absent(label_locator):
                self.scroll_into_view(label_locator)
            time.sleep(1)
            self.button(label_locator)
            if self.is_element_absent(value_locator):
                self.scroll_into_view(value_locator)
            self.button(value_locator)

        except TimeoutException:
            LOG.error("failed to find element {}".format(label_locator[1]))
            raise NoSuchElementException

        except Exception:
            raise

    def deselect(self, drop_down_label):
        '''
        This routine deselects the available option from dropdown
        Args:
            drop_down_label (str): Label of the dropdown
        Returns:
            True or False based on deselecting drop down
        '''

        try:
            index = 1
            self.button(set_locator(
                WD_PF.DROPDOWN.CLEAR_VALUE_XPATH,
                (drop_down_label, str(index))
            ))

            dropdown_text = self.get_text(set_locator(
                WD_PF.DROPDOWN.LABEL_XPATH,
                (drop_down_label, str(index))
            ))

            if drop_down_label in dropdown_text:
                return True
            return False

        except NoSuchElementException:
            return True

        except Exception:
            raise


class Selenium(Dropdown):
    '''base selenium class that abstract all selenium methods'''

    # inherits WebDriver, Browser, Wait, Click, Label, Input and Dropdown
    # Wrapper for all selenium capabilities

    def __init__(self):
        super().__init__()
        self.login()

    @retries
    def login(
            self,
            username=constants.CREDS.USERNAME,
            password=constants.CREDS.DEFAULT_PASSWORD,
    ):
        '''
        Logins to the Application
        Args:
            :username(str): Default: PC_API_CREDS.USERNAME
            :password(str): Default: PC_API_CREDS.COMMON_PASSWORD
        Returns:
            :None:
        '''

        LOG.info("logging in using username: %s password: %s" % (
            username, password
        ))
        self.wait_until_element_present(WD_PF.SELENIUM.USERNAME, timeout=60)
        self.wait_until_element_is_clickable(WD_PF.SELENIUM.USERNAME)
        self.textbox(username, WD_PF.SELENIUM.USERNAME)
        self.button(WD_PF.SELENIUM.PASSWORD)
        self.textbox(password + Keys.ENTER, WD_PF.SELENIUM.PASSWORD)

        self.wait_until_element_is_clickable(
            WD_PF.SELENIUM.SIDE_PANEL, timeout=120
        )
        LOG.info('login successful')

        # The side pannel takes time to load
        # LOG.info("expanding side panel")
        # self.button(WD_PF.SELENIUM.SIDE_PANEL, timeout=60)
        # LOG.info("side panel expanded")
        #
        # # Click on services button
        # LOG.info("expanding services section")
        # self.button(WD_PF.SELENIUM.SERVICES, timeout=60)
        # LOG.info("services section expanded")
        self.load_application_page()

    def load_application_page(self):
        '''
        This routine loads the application page
        '''
        try:
            self.driver.get(self.get_url())
        except (TimeoutException, NoSuchElementException) as e:
            LOG.error(e)

    @retries
    def logout(self):
        '''
        method to logout from PC
        Args:
            :None:
        Raise:
            :Exception: on failure
        '''
        try:
            self.driver.get(self.get_pcurl() + "/console")
        except:
            LOG.info("waiting for /apps page to get opened")
            try:
                self.wait_until_element_present(
                    WD_PF.SELENIUM.SEARCH_INPUT_BOX, timeout=150
                )
            except:
                pass

        self.wait_until_element_present(WD_PF.SELENIUM.ADMIN, timeout=60)
        self.wait_until_element_is_clickable(WD_PF.SELENIUM.ADMIN)
        self.button(WD_PF.SELENIUM.ADMIN)
        self.button(WD_PF.SELENIUM.SIGN_OUT)
        self.wait_until_element_present(WD_PF.SELENIUM.USERNAME, timeout=60)
        self.wait_until_element_present(WD_PF.SELENIUM.PASSWORD, timeout=60)

    def script_text(self, locator, code):
        code_mirror_element = self.driver.find_element(*locator)
        self.driver.execute_script(
            WD_PF.SELENIUM.CM_SET_VALUE, code_mirror_element
        )
        self.driver.execute_script(
            WD_PF.SELENIUM.CM_REPLACE_SELECTION, code_mirror_element, code
        )

    def verify_script_text(self, input_script, script_from_ui):
        '''
        verify whether the script on UI is equal to given input script
        Args:
            :input_script(str): Input script
            :script_from_ui(str): Script which is read from UI
        Returns:
            bool: Verification result
        '''

        input_script_list = input_script.splitlines()
        script_from_ui_list = script_from_ui.splitlines()
        modified_input_script_list = []
        for line in input_script_list:
            if line:
                modified_input_script_list.append(line)
        del input_script_list
        return set(modified_input_script_list).issubset(script_from_ui_list)

    def is_entity_expanded(self, locator):
        '''
        checks whether an entity is expanded or not
        Args:
            :entity_name (str): Name of the entity to be expanded
        Returns:
            :bool: Denotes whether entity needs to be expanded or not
        '''

        return True if "expanded" in self.get_attribute(
            attribute="class", locator=locator
        ) else False

    def toggle_entity(self, locator):
        '''
        toggle an entity collapse if expanded, expand if collapsed
        Args:
            :entity_name (str): Name of the entity to be expanded
        Raises:
            :Exception: on failure
        '''

        self.scroll_from_top(locator)
        self.button(locator)

    def expand_entity(self, expanded_locator, expand_button_locator=None):
        '''
        expand an entity (service, profile, action)
        Args:
            :entity_name (str): Name of the entity to be expanded
        Raises:
            :Exception: on failure
        '''

        if expand_button_locator is None:
            expand_button_locator = expanded_locator

        if not self.is_entity_expanded(expanded_locator):
            self.toggle_entity(expand_button_locator)

    def collapse_entity(self, expanded_locator, expand_button_locator=None):
        '''
        collapse an entity (service, profile, action)
        Args:
            :entity_name (str): Name of the entity to be expanded
        Raises:
            :Exception: on failure
        '''

        if expand_button_locator is None:
            expand_button_locator = expanded_locator

        if self.is_entity_expanded(expanded_locator):
            self.scroll_from_top(expand_button_locator)
            self.toggle_entity(expand_button_locator)

    def expand_section(self, section_name, index=1):
        '''
        This routine will expand the given section name

        Args:
            section_name (str): Section Name
            index (int): Index to the header in case of multiple header with same name

        Return:
            None
        '''

        header_locator = set_locator(
            WD_PF.SELENIUM.SUB_HEADER_DIV, (section_name, index)
        )

        if self.is_element_absent(header_locator):
            header_locator = set_locator(
                WD_PF.SELENIUM.SUB_HEADER_SPAN, (section_name, index)
            )

        self.scroll_from_top(header_locator)

        if "arrow-down" not in self.get_attribute("class", header_locator):
            self.toggle_entity(header_locator)

    def toggle_password(self, show_password):
        """
        This routine hide/display the configured password

        Args:
            show_password(bool): Boolean value indicating show password
        """
        textbox_type = self.get_attribute(
            'type', WD_PF.SELENIUM.SHOW_PASSWORD_INPUT
        )

        if show_password and textbox_type == 'password':
            self.button(WD_PF.SELENIUM.SHOW_PASSWORD)

    def get_element_location(self, locator):
        """
        This routine fetches the location of element in canvas
        Args:
            locator(tuple): web element to fetch location
        Returns:
            dict: location of element in x and y coordinates
        """
        element = self.driver.find_element(*locator)
        return element.location


class Driver:
    def __init__(self):
        '''
        Constructor for Selenium Driver class
        '''

        self.selenium = Selenium()

    def __call__(self):
        self.select_entity()
        return self

    def __enter__(self):
        pass

    def __exit__(self, ty, val, tb):
        pass

    def select_entity(self):
        raise NotImplementedError('object %s has no select_entity method' % str(self))
