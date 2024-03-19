import re
import os
import warnings
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver as webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from bs4 import BeautifulSoup
from datetime import datetime
from dotenv import load_dotenv
import re
import time
from browsermobproxy import Server
import requests

bmp_path = '/Users/nader/Downloads/browsermob-proxy-2.1.4/bin/browsermob-proxy'
server = Server(bmp_path)
server.start()
proxy = server.create_proxy()
# Block the captcha JavaScript file
proxy.blacklist('https://terminvereinbarung.muenchen.de/abh/termin/js/widget.module.min.js', 404)

def get_chrome_options(is_headless=True):
    warnings.filterwarnings(action="ignore")  # Ignore Selenium warnings
    chrome_options = Options()
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if is_headless:
        chrome_options.add_argument("--headless=new")  # Operate Selenium in headless mode
    chrome_options.add_argument("start-maximized") # Required for a maximized Viewport
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation', 'disable-popup-blocking']) # Disable pop-ups to speed up browsing
    chrome_options.add_argument("--window-size=1920x1080") # Set the Chrome window size to 1920 x 1080
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=0")
    chrome_options.add_argument(f'--proxy-server={proxy.proxy}')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    return chrome_options

def init_driver(is_headless):
    print("Instantiate the ChromeDriver")
    chrome_options = get_chrome_options(is_headless)
    capabilities = chrome_options.to_capabilities()
    capabilities['acceptInsecureCerts'] = True
    try:
        driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()), options=chrome_options, desired_capabilities=capabilities)
        print("Succesfully instantiated the ChromeDriver")
        return driver
    except:
        print("Failed to instantiate the ChromeDriver")
        return None
    
def navigate_to_page(driver, base_url):
    try:
        print(f"Navigating to the page: {base_url}")
        driver.get(base_url)
        print("Page loaded successfully.")
    except Exception as e:
        print(f"Exception when navigating to the page: {e}")
        return False
    return True

def switch_to_appointment_frame(driver):
    """Switches to the appointment iframe on the page."""
    try:
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@id='appointment']")))
        return True  # Indicate success
    except Exception as e:
        print(f"Exception when switching to the appointment frame: {e}")
        return False  # Indicate failure

def select_service_dropdown(driver):
    """Selects a service from a dropdown menu, using explicit waits and improved element selection."""
    try:
        # Wait for the dropdown to be clickable
        dropdown_xpath = "//select[@name='CASETYPES[Notfalltermin UA 35]']"
        service_dropdown_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, dropdown_xpath))
        )
        
        # Create Select object for the dropdown and select by index
        Select(service_dropdown_element).select_by_index(1)
        
        return True  # Indicate success
    except Exception as e:
        print(f"Error selecting service from dropdown: {e}")
        return False  # Indicate failure
        
def handle_captcha(driver, api_key, website_url, site_key):
    print("Obtaining the captcha solution token via 2captcha API")
    captcha_task = {
        "clientKey": api_key,
        "task": {
            "type": "FriendlyCaptchaTaskProxyless",
            "websiteURL": website_url,
            "websiteKey": site_key
        }
    }
    
    print("Sending the captcha task to 2captcha")
    response = requests.post("https://api.2captcha.com/createTask", json=captcha_task)
    task_result = response.json()
    
    print("Checking if the captcha task was successfully created")
    if task_result['errorId'] == 0:
        task_id = {"clientKey": api_key, "taskId": task_result['taskId']}
        
        for _ in range(10):  # Polling for the result
            time.sleep(5)
            check_response = requests.post("https://api.2captcha.com/getTaskResult", json=task_id)
            check_result = check_response.json()
            print(f"Checking if the captcha was solved. Status: {check_result['status']}.")
            if check_result['status'] == 'ready':
                token = check_result['solution']['token']
                print("Captcha solved. The token is: ", token)
                
                break
        else:
            print("Failed to solve captcha in time.")
            return False
    else:
        print("Failed to create captcha task.")
        return False
    
    print("Injecting the token into the captcha solution field and handling the captcha")
    try:
        # JavaScript to ensure the captcha solution input exists, set the token, and submit the form
        js_script = f"""
        var captchaInput = document.querySelector('input[name="frc-captcha-solution"]');
        if (!captchaInput) {{
            // If the captcha input doesn't exist, create it
            captchaInput = document.createElement('input');
            captchaInput.setAttribute('type', 'hidden');
            captchaInput.setAttribute('name', 'frc-captcha-solution');
            document.querySelector('form').appendChild(captchaInput);
        }}
        // Set the captcha token
        captchaInput.value = '{token}';

        // Debugging: Log the input value after setting the token
        console.log('Captcha Input Value:', document.querySelector('input[name="frc-captcha-solution"]').value);

        // Submit the form
        document.querySelector('form').submit();
        """

        # Execute the JavaScript
        driver.execute_script(js_script)

        print("Captcha solution injected and form submitted.")
        return True  # Indicate success
    except Exception as e:
        print("Failed to inject the captcha token or submit the form via JavaScript.")
        time.sleep(50)  # Consider whether this delay is necessary or if it should be adjusted based on your needs
        print(f"An error occurred: {e}")
        return False

def output_date_list(driver):
    print("Getting the date list from the webpage.")
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
    print("Extracting the available appointments from the date list.")
    available_appointments = []

    # Ensure that date_list is a DataFrame and not a list, as your function implies
    if not date_list.empty:
        available_df = date_list[date_list["appt_label"] != "Keine freien Termine am"]
        if not available_df.empty:
            available_appointments = available_df['date'].tolist()

    return available_appointments

def kvr_bot():
    try:
        load_dotenv()  # Load environment variables
        is_headless = True
        base_url = os.getenv("BASE_URL")
        api_key = os.getenv("2CAPTCHA_API_KEY")
        site_key = os.getenv("SITE_KEY")
        
        driver = init_driver(is_headless)
        if driver is not None:
            navigate_to_page(driver, base_url)
            switch_to_appointment_frame(driver)
            select_service_dropdown(driver)

            captcha_success = handle_captcha(driver, api_key , base_url, site_key)
            print("Captcha success:", captcha_success)
            if not captcha_success:
                return

            # First, get the date list from the webpage.
            date_list = output_date_list(driver)
            print(date_list)
            
            if date_list is not None:
                available_appointments = extract_available_appointments(date_list)
                print(available_appointments)

            return date_list, available_appointments
        else:
            print("Failed to initialize the driver.")
            return None, None
    
    except Exception as err:
        print(f"An error occurred: {err}")
        return [], []  # It's clearer to return an empty list explicitly if there's an error

    finally:
        if driver is not None:
            driver.quit()  # Ensures the driver quits properly even if there's an error above
            
if __name__ == "__main__":
    kvr_bot()