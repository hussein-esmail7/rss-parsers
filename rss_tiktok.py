'''
rss_tiktok.py
Hussein Esmail
Created: 2021 09 22
Updated: 2021 09 22
Description: [DESCRIPTION]
'''

import os
import sys # To exit the program
from selenium import webdriver
from selenium.common.exceptions import *
# from selenium.webdriver.support.ui import Select  # Used to select from drop down menus
from selenium.webdriver.chrome.options import Options  # Used to add aditional settings (ex. run in background)
# from selenium.webdriver.common.keys import Keys  # Used for pressing special keys, like 'enter'
import platform
import time

bool_use_Brave = False
bool_run_in_background = False
os_type = platform.platform().split("-")[0]
path_urls = os.path.expanduser("~/Documents/Local-RSS/TikTok/urls")
if os_type == "Linux":
    chromedriver_path = os.path.expanduser("~/Documents/Coding/py/reference/Chromedriver/chromedriver")
elif os_type == "macOS":
    chromedriver_path = "/Users/hussein/Documents/Coding/py/reference/Chromedriver/chromedriver"
target_site = "https://www.tiktok.com/@nothanksalex"

def main():
    options = Options()  
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    if bool_use_Brave:
        options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Chrome(chromedriver_path, options=options)
    driver.get(target_site)
    vid_links = [] 
    temp = driver.find_elements_by_class_name("video-feed-item-wrapper")
    print(len(temp))
    for i in temp:
        vid_links.append(i.get_attribute('href')) # Video links

    print("\n".join(vid_links))
    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set
    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
