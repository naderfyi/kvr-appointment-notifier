import os
from twocaptcha import TwoCaptcha
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global inputs
base_url = "https://stadt.muenchen.de/terminvereinbarung_/terminvereinbarung_abh.html?cts=1000113&fbclid=IwAR31BvMBVLqWDBmoJweBxakVchV3CUbu17dKrNQQPheUVk2502k73BgckcY"
solver = TwoCaptcha(os.getenv("2CAPTCHA_API_KEY")) # Will be used to solve the image captcha
is_headless = True # Set to True if you want to run the bot in headless mode

# Captcha solver inputs
image_captcha_phrase = 0 # Helper field for the 2Captcha solver. 0 - captcha contains one word. 1 - captcha contains two or more words
image_captcha_min_len = 3 # Helper field for the 2Captcha solver. 0 - not specified. 1..20 - minimal number of symbols in captcha
image_captcha_max_len = 5 # Helper field for the 2Captcha solver. 0 - not specified. 1..20 - maximum number of symbols in captcha
image_captcha_case_sensitive = 1 # Helper field for the 2Captcha solver. 0 - Case insensitive. 1 - Case sensitive
default_captcha_img_name = "captcha_img" # Name of the captcha image file that gets downloaded from the website
img_captcha_trials = 5 # Number of times to retry solving the image captcha if the first attempt fails
if is_headless:
    x_coordinate = 20 # Left coordinate of the captcha image on the website (x). Needs to be hard-coded as dynamic crawling yields incorrect coordinates
    y_coordinate = 520 # Top coordinate of the captcha image on the website (y). Needs to be hard-coded as dynamic crawling yields incorrect coordinates
else:
    x_coordinate = 45 # Left coordinate of the captcha image on the website (x). Needs to be hard-coded as dynamic crawling yields incorrect coordinates
    y_coordinate = 535 # Top coordinate of the captcha image on the website (y). Needs to be hard-coded as dynamic crawling yields incorrect coordinates