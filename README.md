# kvr_termin_bot
This repo contains a Python script that tracks the availability of appointments on [Munich's KVR website](https://stadt.muenchen.de/terminvereinbarung_/terminvereinbarung_abh.html?cts=1000113&fbclid=IwAR31BvMBVLqWDBmoJweBxakVchV3CUbu17dKrNQQPheUVk2502k73BgckcY)

# How to operate the bot?
1- **Clone the repo** using the command `git clone https://github.com/naderfyi/kvr_termin_bot.git`  
2- **Install the dependencies** with `pip install -r requirements.txt`  
3- **Create a 2Captcha account** [here](https://2captcha.com/) and fill up your balance. 5 to 10 EUR is enough and should last you a long time  
4- **Create a .env file** in your local directory where you cloned the repo and add the following variable --> `2CAPTCHA_API_KEY="..."`. Replace the dots with the 2Captcha API key  
5- Define whether or not you want to operate the bot in **headless** mode by changing the variable `is_headless` in `inputs.py`  
6- In your terminal, type in the following command to **run the bot** --> `python bot.py`  

The bot will run and print out a status message saying **whether or not there are appointments**. If there are appointments, it will print out the **specific dates when appointments exist.**