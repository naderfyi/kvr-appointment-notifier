import os
from PIL import Image
from selenium.webdriver.common.by import By

def download_captcha_img(captcha_img_name, captcha_selector, left, top, driver):
    """
    Downloads and crops the captcha image from the website.

    :param captcha_img_name: Name of the captcha image file.
    :param captcha_selector: XPath selector for the captcha image element.
    :param left: Left coordinate for the cropping area.
    :param top: Top coordinate for the cropping area.
    :param driver: Selenium WebDriver instance.
    """
    try:
        captcha_element = driver.find_element(By.XPATH, captcha_selector)
        right, bottom = calculate_captcha_dimensions(captcha_element, left, top)

        screenshot_filename = f"{captcha_img_name}.png"
        driver.save_screenshot(screenshot_filename)

        crop_screenshot_to_captcha(screenshot_filename, (left, top, right, bottom))
    except Exception as e:
        print(f"An error occurred while downloading the captcha image: {e}")

def calculate_captcha_dimensions(captcha_element, left, top):
    """Calculate the dimensions for the captcha based on the element's size."""
    width = captcha_element.size['width']
    height = captcha_element.size['height']
    return left + width, top + height

def crop_screenshot_to_captcha(screenshot_filename, box):
    """Crop the screenshot to only include the captcha based on the provided box dimensions."""
    with Image.open(screenshot_filename) as im:
        print("Cropping the screenshot to the exact captcha image dimensions.")
        im_cropped = im.crop(box)
        im_cropped.save(screenshot_filename)

def solve_image_captcha_2captcha(solver, captcha_img_name, phrase, min_len, max_len, case_sensitive):
    """
    Solves the image captcha using the 2captcha service and deletes the image file afterward.

    :param solver: The 2captcha solver instance.
    :param captcha_img_name: The name of the captcha image file.
    :param phrase: Specifies if the captcha contains one or more words.
    :param min_len: The minimum number of symbols in the captcha.
    :param max_len: The maximum number of symbols in the captcha.
    :param case_sensitive: Whether the captcha solution is case sensitive.
    :return: The captcha key if solved, else None.
    """
    captcha_key = None
    filepath = os.path.join(os.getcwd(), f"{captcha_img_name}.png")

    try:
        # Attempt to solve the captcha
        result = solver.normal(file=filepath, phrase=phrase, 
                               minLen=min_len, maxLen=max_len, 
                               caseSensitive=case_sensitive)
        captcha_key = result.get('code')

        print(f"Captcha solved. The key is: {captcha_key}")

    except Exception as err:
        # Log the exception if captcha solving failed
        print(f"Captcha not solved. The error is {err}")

    finally:
        # Whether solved or not, delete the captcha image as it's no longer needed
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Captcha image '{captcha_img_name}.png' has been deleted.")
        except Exception as e:
            # Handle potential exception from file deletion
            print(f"Failed to delete captcha image. Reason: {e}")

    return captcha_key