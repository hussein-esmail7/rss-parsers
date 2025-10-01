'''
rss_danu.py
Hussein Esmail
Created: 2025 09 30
Updated: 2025 09 30
Description: [DESCRIPTION]
'''

# This part is used for https://github.com/hussein-esmail7/template-maker
# templateDescription: Python Selenium Web Scraper

import os
import time
import sys # To exit the program
from bs4 import BeautifulSoup, Tag, NavigableString
import requests
from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import Select  # Used to select from drop down menus
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)
# from selenium.webdriver.common.keys import Keys  # Used for pressing special keys, like 'enter'

# ========= VARIABLES ===========
bool_run_in_background  = True
bool_prints             = True
target_site             = "https://www.danusocialhouse.ca/events"

# ========= COLOR CODES =========
color_end               = '\033[0m'
color_darkgrey          = '\033[90m'
color_red               = '\033[91m'
color_green             = '\033[92m'
color_yellow            = '\033[93m'
color_blue              = '\033[94m'
color_pink              = '\033[95m'
color_cyan              = '\033[96m'
color_white             = '\033[97m'
color_grey              = '\033[98m'

# ========= COLORED STRINGS =========
str_prefix_q            = f"[{color_pink}Q{color_end}]\t "
str_prefix_y_n          = f"[{color_pink}y/n{color_end}]"
str_prefix_err          = f"[{color_red}ERROR{color_end}]\t "
str_prefix_done         = f"[{color_green}DONE{color_end}]\t "
str_prefix_info         = f"[{color_cyan}INFO{color_end}]\t "

def main():
    # ADDITIONAL CODE HERE
    # Example of getting elements by XPATH
    # time_unformatted = driver.find_element(By.XPATH, '//time/span[1]').text + " /" + driver.                find_element(By.XPATH, '//time/span[2]').text¬
    # options = Options()
    # if bool_run_in_background:
    #     options.add_argument("--headless")  # Adds the argument that hides the window
    # service = Service(ChromeDriverManager.install(self))
    # driver = webdriver.Chrome(service=service, options=options)
    # driver = webdriver.Chrome(options=options)
    # driver.set_window_size(200, 1000) # Window size
    driver = webdriver.Chrome()
    driver.get(target_site)
    driver.implicitly_wait(0.5)

    events_list = driver.find_elements(By.CLASS_NAME, 'event-collection-item')
    if bool_prints:
        print(f"{str_prefix_info} # of event list items: {len(events_list)}")

    for event in events_list:
        event_url = event.find_element(By.TAG_NAME, 'a').get_attribute('href')
        event_title = event.find_element(By.CLASS_NAME, 'event-card-title').text
        event_date = event.find_element(By.CLASS_NAME, 'event-card-title').text

    dummy = input("> ")
    # soup = BeautifulSoup(driver.page_source, 'lxml')
    # d = soup.find('div', attrs= {'class': 'event-collection-item'})
    # print(d.text.strip())

    # Cleanup
    driver.close()  # Close the browser
    # options.extensions.clear() # Clear the options that were set
    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
