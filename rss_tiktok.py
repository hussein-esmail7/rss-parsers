'''
rss_tiktok.py
Hussein Esmail
Created: 2021 09 22
Updated: 2021 09 22
Description: [DESCRIPTION]
'''

# This part is used for https://github.com/hussein-esmail7/template-maker
# templateDescription: Python Selenium Web Scraper

import os
import sys # To exit the program
from selenium import webdriver
from selenium.common.exceptions import *
# from selenium.webdriver.support.ui import Select  # Used to select from drop down menus
from selenium.webdriver.chrome.options import Options  # Used to add aditional settings (ex. run in background)
# from selenium.webdriver.common.keys import Keys  # Used for pressing special keys, like 'enter'

bool_use_Brave = False
bool_run_in_background = False
chromedriver_path = os.path.expanduser("~/Documents/Coding/py/reference/Chromedriver/chromedriver")
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
    vid_elements = driver.find_elements_by_class_name("video-feed-item")
    vid_links = driver.find_elements_by_class_name("video-feed-item-wrapper")
    for i in vid_links:
        print(i.get_attribute('href')) # Video links
    print(len(vid_elements))
    dummy = input(">")

    # ADDITIONAL CODE HERE

    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set
    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
