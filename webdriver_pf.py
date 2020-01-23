from selenium.webdriver.common.by import By


class DROPDOWN:
    COMMON = "//label[text()='%s']/div"
    CLEAR_VALUE = "//span[@title='Clear value']"
    CLEAR_ALL = "//span[@title='Clear all']"
    LABEL_XPATH = By.XPATH, "(//label[text()='%s']/div)[%s]"
    CLEAR_VALUE_XPATH = By.XPATH, LABEL_XPATH[1] + CLEAR_VALUE
    CLEAR_ALL_XPATH = By.XPATH, LABEL_XPATH[1] + CLEAR_ALL
    DROPDOWN_ICON = By.XPATH, "//span[@class='Select-arrow']"
    SELECT_OPTIONS_XPATH = By.XPATH, "//div[@class='Select-menu-outer']"
    SELECT_OPTIONS_VALUE = By.XPATH, "//div[@class='Select-value']"
    SELECT_VALUE_XPATH = By.XPATH, SELECT_OPTIONS_XPATH[1] + "//*[contains(text(), '%s')]"
    SELECT_VALUE = By.XPATH, SELECT_OPTIONS_VALUE[1] + "//*[contains(text(), '%s')]"
    SELECT_ARROW_XPATH = By.XPATH, "//label[text()='%s']//div[@class='Select-control']//span[@class='Select-arrow']"
    SELECT_ARROW_IDX_XPATH = By.XPATH, SELECT_ARROW_XPATH[1]+ "[%s]"
    SELECT_INPUT_XPATH = By.XPATH, "//label[text()='%s']//div[@class='Select-input']//input"


class SELENIUM:
    # login and logout locators
    USERNAME = By.ID, "inputUsername"
    PASSWORD = By.ID, "inputPassword"
    SIDE_PANEL = By.XPATH, "//div[@class='header-hamburger-button-slice']"
    SERVICES = By.XPATH, "//a[text()='Services']"
    SEARCH_INPUT_BOX = By.XPATH, "//input[contains(@class ,'searchelement__input')]"
    ADMIN = By.XPATH, "//a/span[@class='n-username']"
    SIGN_OUT = By.LINK_TEXT, "Sign Out"
    CLOSE = By.XPATH, "//button[@class='modal-close']"

    # other methods
    CM_SET_VALUE = "arguments[0].CodeMirror.setValue('');"
    CM_REPLACE_SELECTION = "arguments[0].CodeMirror.replaceSelection(arguments[1], null, '+input');"
    SUB_HEADER_DIV = By.XPATH, "(//div[contains(text(), '%s')]/../div[1])[%d]"
    SUB_HEADER_SPAN = By.XPATH, "(//span[contains(text(), '%s')]/../div[1])[%d]"
    SHOW_PASSWORD_INPUT = By.XPATH, "//button[@class='password-input-show-icon']/../input"
    SHOW_PASSWORD = By.XPATH, "//button[@class='password-input-show-icon']"
