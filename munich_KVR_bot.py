# Import the packages
import re
import warnings
from datetime import datetime

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver as webdriver_vanilla
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

from helper_functions import download_captcha_img, solve_image_captcha_2captcha
from inputs import *

warnings.filterwarnings(action="ignore")

###----------------------------------###----------------------------------###

# Set the Chrome options
chrome_options = Options()
chrome_options.add_argument("start-maximized") # Required for a maximized Viewport
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation', 'disable-popup-blocking']) # Disable pop-ups to speed up browsing
chrome_options.add_experimental_option("detach", True) # Keeps the Chrome window open after all the Selenium commands/operations are performed 
chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'}) # Operate Chrome using English as the main language
if is_headless:
    chrome_options.add_argument("--headless=new") # Operate Selenium in headless mode
chrome_options.add_argument('--disable-extensions') # Disable extensions
chrome_options.add_argument('--no-sandbox') # Disables the sandbox for all process types that are normally sandboxed. Meant to be used as a browser-level switch for testing purposes only
chrome_options.add_argument('--disable-gpu') # An additional Selenium setting for headless to work properly, although for newer Selenium versions, it's not needed anymore
chrome_options.add_argument("--window-size=1920x1080") # Set the Chrome window size to 1920 x 1080

###----------------------------------###----------------------------------###

from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from datetime import datetime
import re

def setup_webdriver():
    print("Instantiate the ChromeDriver")
    driver = webdriver_vanilla.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()), options=chrome_options)
    return driver

def navigate_to_page(driver, base_url):
    print("Navigate to the base_url")
    driver.get(base_url)
    driver.maximize_window()

def switch_to_appointment_frame(driver):
    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@id='appointment']")))

def select_service_dropdown(driver):
    service_dropdown = Select(driver.find_element(by=By.XPATH, value="//select[@name='CASETYPES[Notfalltermin UA 35]']"))
    service_dropdown.select_by_index(1)

def handle_captcha(driver, solver):
    img_captcha_solved = False
    img_captcha_counter = 1
    while not img_captcha_solved and img_captcha_counter <= img_captcha_trials:
        print(f"Attempt #{img_captcha_counter} to solve the image captcha. Downloading the captcha image...")
        download_captcha_img(captcha_img_name=default_captcha_img_name, captcha_selector="//img[@id='captchai']", left=x_coordinate, top=y_coordinate, driver=driver)
        
        img_captcha_key = solve_image_captcha_2captcha(solver=solver, captcha_img_name=default_captcha_img_name, phrase=image_captcha_phrase, min_len=image_captcha_min_len, max_len=image_captcha_max_len, case_sensitive=image_captcha_case_sensitive)

        captcha_input_field = driver.find_element(by=By.XPATH, value="//input[@name='captcha_code']")
        captcha_input_field.send_keys(img_captcha_key)
        driver.find_element(by=By.XPATH, value="//input[@class='WEB_APPOINT_FORWARDBUTTON']").click()

        try:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//span[@class='navMonthText']")))
            img_captcha_solved = True
        except TimeoutException:
            print(f"The image captcha was not solved correctly. Proceeding to trial number {img_captcha_counter} out of {img_captcha_trials}...")
            img_captcha_counter += 1
            driver.find_element(by=By.XPATH, value="//a[@onclick='loadImage(); return false;']").click()
            captcha_input_field.clear()

        if img_captcha_counter > img_captcha_trials:
            print(f"The image captcha was not solved correctly after {img_captcha_trials} trials. Exiting the program...")
            driver.quit()
            return False

    return True

def output_date_list(driver):
    date_list = []
    soup = BeautifulSoup(driver.page_source, "html.parser")
    appt_dates = soup.select(selector="td.nat_calendar")

    for app in appt_dates:
        try:
            appt_label = app.select_one("span:first-of-type").get_text().strip()
            appt_label_plus_date = app.get_text().strip()
            date_str = re.findall(r"[\d\.]+", appt_label_plus_date)[0]  # This assumes the date is always present
            date = datetime.strptime(date_str, "%d.%m.%Y").date()

            date_list.append({"appt_label": appt_label, "date": date})
            
        except Exception as e:  # This catches any exception, consider logging it.
            date_list.append({"appt_label": None, "date": None})

    # Create the DataFrame after constructing the list
    df_dates = pd.DataFrame(date_list)
    df_valid_dates = df_dates[df_dates["appt_label"].notnull()].reset_index(drop=True)

    return df_valid_dates

def extract_available_appointments(date_list):
    available_appointments = []

    # Ensure that date_list is a DataFrame and not a list, as your function implies
    if not date_list.empty:
        available_df = date_list[date_list["appt_label"] != "Keine freien Termine am"]
        if not available_df.empty:
            available_appointments = available_df['date'].tolist()

    return available_appointments


def kvr_bot():
    try:
        driver = setup_webdriver()
        navigate_to_page(driver, base_url)

        switch_to_appointment_frame(driver)
        select_service_dropdown(driver)

        captcha_success = handle_captcha(driver, solver)
        if not captcha_success:
            return

        # First, get the date list from the webpage.
        date_list = output_date_list(driver)
        
        if date_list is not None:
            available_appointments = extract_available_appointments(date_list)

        return date_list, available_appointments

    except Exception as err:
        print(f"An error occurred: {err}")
        return [], []  # It's clearer to return an empty list explicitly if there's an error

    finally:
        if driver is not None:
            driver.quit()  # Ensures the driver quits properly even if there's an error above