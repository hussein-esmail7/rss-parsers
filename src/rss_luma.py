'''
rss_luma.py
Hussein Esmail
Created: 2026 01 25
Updated: 2026 01 25
Description: [DESCRIPTION]
'''

# This part is used for https://github.com/hussein-esmail7/template-maker
# templateDescription: Python Selenium Web Scraper

import os
import sys # To exit the program
import datetime
import time
from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import Select  # Used to select from drop down menus
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)
# from selenium.webdriver.common.keys import Keys  # Used for pressing special keys, like 'enter'

# ========= VARIABLES ===========
bool_prints             = False
bool_run_in_background  = False
target_site             = "https://luma.com/1rg-calendar"
str_members_only        = "----- MEMBERS ONLY -----\n\n"

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

def most_recent_date(unprocessed: str, weekday: int, str_format: str, start_year: int):
    # This recursive function is designed to get the most recent date that is
    # correct to the weekday.
    # The reason this program exists is because I am given a month, day, and
    # weekday but the datetime package is returning information from the year
    # 1900 when it is supposed to be for this year.
    # INPUT VALUE EXAMPLES:
    # unprocessed: "Jan 25"
    # weekday: 6 (Mon = 0, Sun = 6)
    # str_format: "%b %d" (must match 'unprocessed' string)
    # start_year: 2026, or datetime.datetime.now().year
    check = datetime.datetime.strptime(unprocessed.strip() + " " + str(start_year), str_format + " %Y")
    if check.weekday() == weekday:
        return check
    else:
        return most_recent_date(unprocessed, weekday, str_format, start_year-1)

def main():
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(200, 1000) # Window size
    driver.get(target_site)

    # Used to download HTML file
    # html_source_code = driver.execute_script("return document.body.innerHTML;")
    # file_name = datetime.datetime.now().strftime("%Y %m %d %H%M%S") + " luma html.txt"
    # print(html_source_code)
    # os.chdir("/Users/hussein/Downloads/")
    # with open(file_name, "w") as text_file:
    #     text_file.write(html_source_code)
    #     print(f"{str_prefix_info} HTML code written to file {file_name} in {os.getcwd()}")

    events_list = driver.find_element(By.CLASS_NAME, 'schedule')
    # 'events_list': The entire main content (not the right column that normally
    # holds the calendar, image of a map, etc.
    events_list = events_list.find_element(By.CLASS_NAME, 'jsx-3332215563')
    # Get the last div element in 'schedule'.
    # The first is normally the "Events" text
    # The second is normally filterable tags like "Members Only"
    # There can be others in between
    # Getting the last element is the best choice because it's length is
    # dependent on how many events there are. Good practice on Luma's side
    events_list = events_list.find_element(By.CLASS_NAME, 'timeline') # div.timeline

    # events_list = events_list.find_elements(By.TAG_NAME, 'div')[0] # div.timeline
    # 1 element deeper. There was previously an issue searching for the
    # 'timeline' class.
    #NOTE: events_list = events_list_copy.find_elements(By.CLASS_NAME, 'timeline-section') # 12 when there's only 10
    events_list = events_list.find_elements(By.XPATH, './/div[contains(@class, "timeline-section")]')
    # Entries in this list is for each day. There can be multiple events in
    # each day (i.e. nested for loop. The outer for every day, the inner for
    # every event on that day)
    print(f"{str_prefix_info} Number of items found by searching 'timeline-section': {len(events_list)}")
    qty_events_list_1 = len(events_list)
    time.sleep(5)
    # TODO: Need time for the entire page to load.
    for num, event_day in enumerate(events_list):
        # This loop is needed because for some reason it's finding 3 more
        # elements than the number that already exists.
        # Only getting ones without error from this list
        try:
            date_unprocessed = event_day.find_element(By.CLASS_NAME, 'date').text
            print(f"          Run #{num+1}/{len(events_list)}: {date_unprocessed}")
            # 'date_unprocessed' is named this way because it will be
            # eventually be put into the datetime library to get the full date
        except:
            events_list.remove(event_day)
    qty_events_list_2 = len(events_list)
    if bool_prints:
        if qty_events_list_1 == qty_events_list_2:
            print(f"{str_prefix_info} Quantity unchanged")
        else:
            print(f"{str_prefix_info} Quantity reduced from {qty_events_list_1} to {qty_events_list_2}")

    # dummy = input(f"{str_prefix_info} CHECK QUANTITIES > ")
    array_events = []
    for num, event_day in enumerate(events_list):
        # This is the actual outer loop to get the information
        print(f"{str_prefix_info} Run #{num+1}/{len(events_list)}")
        date_unprocessed = event_day.find_element(By.XPATH, ".//div[contains(@class, 'title')]").text.split("\n")[0]
        date_unprocessed_weekday = event_day.find_element(By.XPATH, ".//div[contains(@class, 'title')]").text.split("\n")[-1]
        if "Today" in date_unprocessed:
            date_processed = datetime.datetime.now()
        else:
            date_processed = most_recent_date(date_unprocessed, time.strptime(date_unprocessed_weekday, "%A").tm_wday, "%b %d", datetime.datetime.now().year)
        print(f"\t  {date_processed.strftime("%Y %m %d (%a)")}")
        # ----------------------------------
        dummy = input(f"{str_prefix_info} Confirmed working until here > ")
        # ----------------------------------
        # TODO: Confirmed working until here
        # ----------------------------------
        list_events = event_day.find_elements(By.XPATH, ".//div[contains(@class, 'flex-1')]")
        # 'list_events': All the events that happen in that one day
        if len(list_events) == 0:
            print(f"{str_prefix_err} No events found on this day.")
        for num_event, event in enumerate(list_events):
            item = event.find_element(By.XPATH, ".//div[contains(@class, 'card-wrapper')]")
            item = item.find_element(By.XPATH, ".//div")
            url = item.find_element(By.TAG_NAME, "a").get_attribute('href')
            title = item.find_element(By.TAG_NAME, "a").get_attribute('aria-label')
            # item = item.find_element(By.XPATH, ".//div[contains(@class, 'event-content'])")
            item = item.find_element(By.TAG_NAME, "div")
            print(title)
            print(url)
            info = item.find_element(By.XPATH, ".//div/div[contains(@class, 'info-and-cover')]/div[contains(@class, 'info')]")
            time_text = info.find_element(By.XPATH, ".//div[contains(@class, 'event-time')]").text # Ex. "7:00 PM"
            print(time)
            location = info.find_element(By.XPATH, ".//div[contains(@class, 'gap-1')]/div[2]/div[contains(@class, 'text-ellipses')]").text
            print(location)
            # TODO: Decide if I want to get the location now or when each URL is visited
            description = ""
            if "Members Only" in info.text:
                description = str_members_only
            array_events.append({
                'title': title,
                'time': time_text,
                'url': url,
                'location': location,
                'price': 0, # TODO
                'description': description
                })


    dummy = input(f"{str_prefix_info} Program is up to date. Press enter to quit > ")

    # Example of getting elements by XPATH -----------------------------------
    # ITEM = driver.find_element(By.XPATH, '//time/span[1]')        # singular
    # ITEM = driver.find_elements(By.XPATH, '//time/span[1]')        # n items
    # Example of getting elements by CLASS_NAME ------------------------------
    # ITEM = driver.find_element(By.CLASS_NAME, 'schedule')         # singular
    # ITEM = driver.find_elements(By.CLASS_NAME, 'schedule')         # n items
    # Example of getting elements by ID --------------------------------------
    # ITEM = driver.find_element(By.ID, 'schedule')                 # singular
    # ITEM = driver.find_elements(By.ID, 'schedule')                 # n items
    # Example of getting elements by TAG_NAME --------------------------------
    # ITEM = driver.find_element(By.TAG_NAME, 'div')                # singular
    # ITEM = driver.find_elements(By.TAG_NAME, 'div')                # n items
    # Example of getting text from an element --------------------------------
    # ITEM = driver.find_element(By.CLASS_NAME, 'schedule').text
    # NOTE: If .text is run on a list, it may give an error or parse the entire
    #   thing by itself. Best to run this in a loop if doing it for every
    #   element.

    # dummy = input("Program is up to date. Press enter to quit > ")
    # Put this line where you need to have time to inspect the site
    # If printing information to process, print it before this 'dummy' line.
    # The final finished program should not have this line by the time you're
    # dont writing it, only for purposes while writing the program

    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set
    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
