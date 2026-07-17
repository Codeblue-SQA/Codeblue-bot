import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class SignsIncLeadPage:

    NAME_INPUT      = (By.XPATH, "//label[contains(., 'Full Name')]/following::input[1]")
    EMAIL_INPUT     = (By.XPATH, "//label[contains(., 'Email Address')]/following::input[1]")
    PHONE_INPUT     = (By.XPATH, "//label[contains(., 'Phone Number')]/following::input[1]")
    DETAILS_TEXTAREA= (By.XPATH, "//label[contains(., 'Details')]/following::textarea[1]")

    PLACEMENT_INDOOR  = (By.XPATH, "//*[contains(text(), 'INDOOR')]")
    PLACEMENT_OUTDOOR = (By.XPATH, "//*[contains(text(), 'OUTDOOR')]")

    FILE_INPUT  = (By.CSS_SELECTOR, "input[type='file']")

    SUBMIT_BTN  = (By.CSS_SELECTOR, "button.submitButton_at_lead")
    SUCCESS_DIV = (By.ID, "submitSuccess_at_lead")

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)  
        self.submission_time_seconds = None

    def open(self, url: str):
        self.driver.get(url)
        self.wait.until(EC.presence_of_element_located(self.SUBMIT_BTN))

    def fill_name(self, value: str):
        self._type(self.NAME_INPUT, value)

    def fill_email(self, value: str):
        self._type(self.EMAIL_INPUT, value)

    def fill_phone(self, value: str):
        self._type(self.PHONE_INPUT, value)

    def fill_details(self, value: str):
        self._type(self.DETAILS_TEXTAREA, value)

    def select_placements(self, indoor=True, outdoor=False):
        if indoor:
            self._check(self.PLACEMENT_INDOOR)
        if outdoor:
            self._check(self.PLACEMENT_OUTDOOR)

    def select_mockup_types(self, mockup_id: str):
        locator = (By.XPATH, f"//label[@for='{mockup_id}']")
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)

    def upload_image(self, path: str):
        el = self.wait.until(EC.presence_of_element_located(self.FILE_INPUT))
        self.driver.execute_script("arguments[0].style.display = 'block';", el)
        el.send_keys(path)

    def submit(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.5) 

        submit_start = time.time()
        self.driver.execute_script("""
            var evt = new MouseEvent('click', {bubbles: true, cancelable: true, view: window});
            arguments[0].dispatchEvent(evt);
        """, btn)

        try:
            self.wait.until(lambda d: "d-none" not in d.find_element(
                By.ID, "submitSuccess_at_lead").get_attribute("class")
            )
        except TimeoutException:
            pass
        finally:
            self.submission_time_seconds = round(time.time() - submit_start, 2)

    def get_submission_duration(self) -> float | None:
        return self.submission_time_seconds

    def success_visible(self) -> bool:
        try:
            el = self.wait.until(EC.presence_of_element_located(self.SUCCESS_DIV))
            return "d-none" not in el.get_attribute("class")
        except:
            return False

    def _type(self, locator, value: str):
        el = self.wait.until(EC.visibility_of_element_located(locator))
        el.clear()
        el.send_keys(value)

    def _check(self, locator):
        el = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].click();", el)