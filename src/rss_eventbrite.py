'''
rss_eventbrite.py
Hussein Esmail
Created: 2023 08 04 (Mon)
Updated: 2023 08 04 (Mon)
Description: RSS Parser for Eventbrite
'''

import os
import re # Regex used to get integer from "Upcoming (18)" to determine real target numbers
import sys # To exit the program
import time
from selenium import webdriver
from selenium.common.exceptions import *
import logging
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import Select  # Used to select from drop down menus
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)
# from selenium.webdriver.common.keys import Keys  # Used for pressing special keys, like 'enter'
import urllib.request # To check internet connection and download urls
import datetime
from dateutil.relativedelta import relativedelta
import to_rss # Python function file in same directory

# ========= VARIABLES ===========
bool_run_in_background  = False # TODO
bool_prints = True
target_site             = "https://www.eventbrite.ca/o/changeling-gaming-events-toronto-74160242103"
# TODO: Convert to a parametric url list (referred to in config folder) rather than hardcoded
RSS_TITLE = "TODO - Eventbrite"
RSS_DESCRIPTION = "TODO - Eventbrite"

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

def is_internet_connected():
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
        return False

def get_past_date(str_days_ago):
    # https://stackoverflow.com/a/43139601/8100123
    # This function returns a datetime object 'n' days ago
    # if you input "n days ago" (which is how TAPA formats posted dates)
    TODAY = datetime.date.today()
    splitted = str_days_ago.split()
    if len(splitted) == 1 and splitted[0].lower() == 'today':
        return str(TODAY.isoformat())
    elif len(splitted) == 1 and splitted[0].lower() == 'yesterday':
        date = TODAY - relativedelta(days=1)
        return str(date.isoformat())
    elif splitted[1].lower() in ['hour', 'hours', 'hr', 'hrs', 'h']:
        date = datetime.datetime.now() - relativedelta(hours=int(splitted[0]))
        return str(date.date().isoformat())
    elif splitted[1].lower() in ['day', 'days', 'd']:
        date = TODAY - relativedelta(days=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['wk', 'wks', 'week', 'weeks', 'w']:
        date = TODAY - relativedelta(weeks=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['mon', 'mons', 'month', 'months', 'm']:
        date = TODAY - relativedelta(months=int(splitted[0]))
        return str(date.isoformat())
    elif splitted[1].lower() in ['yrs', 'yr', 'years', 'year', 'y']:
        date = TODAY - relativedelta(years=int(splitted[0]))
        return str(date.isoformat())
    else:
        print("ERROR in 'get_past_date()': Wrong Argument format: " + str_days_ago)
        sys.exit(2)


def main():
    rss_path = "~/.config/rss-parsers/Eventbrite/changeling.xml"
    int_new_postings = 0
    if not is_internet_connected():
        print(f"{str_prefix_err}You're not connected to the internet!")
        sys.exit(1)

    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Run in background
    os.environ['WDM_LOG'] = str(logging.NOTSET) # Do not output logs for CDM
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(200, 1000) # Window size
    driver.get(target_site)
    to_rss.create_rss(path=rss_path, title=RSS_TITLE, subtitle=RSS_DESCRIPTION)

    # Getting the hardcoded number of upcoming future events
    # This is so that if the number is greater than the number of events
    # actually found, go back and scroll to the bottom of the page and re-run
    # that part
    num_events_future_tmp = driver.find_element(By.CLASS_NAME, "eds-tabs__content--upcoming-events-title").text
    num_events_future_real = int(re.search(r'\d+', num_events_future_tmp).group())
    print(f"Actual future events: {num_events_future_real}")

    # num_events_future_found = 0
    # Run this code once begore getting into the while loop
    a = driver.find_element(By.CLASS_NAME, "eds-tabs__content--upcoming-events")
    b = a.find_element(By.XPATH, "div/div[2]")
    c = b.find_elements(By.CLASS_NAME, "eds-l-pad-vert-2")
    e_events_future = c
    num_events_future_found = len(e_events_future)
    while num_events_future_found < num_events_future_real:
        if driver.find_elements(By.CLASS_NAME, "organizer-profile__show-more"):
            btn_show_more = driver.find_elements(By.CLASS_NAME, "organizer-profile__show-more")[0].find_element(By.XPATH, "button").click()
            time.sleep(2)
        # Getting the element list of future events
        a = driver.find_element(By.CLASS_NAME, "eds-tabs__content--upcoming-events")
        b = a.find_element(By.XPATH, "div/div[2]")
        c = b.find_elements(By.CLASS_NAME, "eds-l-pad-vert-2")
        e_events_future = c
        num_events_future_found = len(e_events_future)
    print(f"Found future events: {num_events_future_found}")
    events_future = []
    for event_future in e_events_future:
        tmp_event = event_future.find_element(By.XPATH, "div")
        image = tmp_event.find_element(By.XPATH, "a/div/img").get_attribute("src") # Image URL
        url = tmp_event.find_element(By.XPATH, "a").get_attribute("href") # Event URL
        title = tmp_event.find_element(By.XPATH, "section/div/h3").text # Event title
        date = tmp_event.find_element(By.XPATH, "section/div/p[1]").text # Event title
        location_name = tmp_event.find_element(By.XPATH, "section/div/p[2]").text # May just be the title of the location, not the address
        events_future.append({
            'title': title,
            'image': image,
            'url': url,
            'date': date,
            'location_name': location_name,
            'location_address': "TODO"
            })
    print("Checking each URL for all dates and addresses now...")
    for event in events_future:
        # In this loop, get address of each event, as well as all the times if
        # the header previously had a "+" in the string
        driver.get(event['url'])
        time.sleep(0.5)
        loc_full = driver.find_element(By.CLASS_NAME, "location-info__address").text
        loc_name = driver.find_element(By.CLASS_NAME, "location-info__address-text").text
        loc_addr = loc_full.replace(loc_name, "").strip().split('\n')[0]
        event['location_address'] = loc_addr # Update array
        # Now dealing with the ones with multiple dates on one page/entry
        if "+" in event['date']:
            # dummy = input("DATE NEED ON THIS URL > ") # -----------///////////
            # while not driver.find_elements(By.CLASS_NAME, "child-event-dates-item"):
            date_list = driver.find_elements(By.CLASS_NAME, "child-event-dates-item")
            alldates = []
            for date_item in date_list:
                indiv_event_date = date_item.find_element(By.XPATH, "div/button/div/time").get_attribute('datetime')
                events_future.append({
                    'title': event['title'],
                    'image': event['image'],
                    'url': event['url'],
                    'date': indiv_event_date,
                    'location_name': event['location_name'],
                    'location_address': event['location_address']
                    })
            del event

    # TODO: Verify the "+ 2 more" (+etc) entries are deleted after each individual date entry is added
    # TODO: Convert date formats to ISO so it can be sorted by that later (before sending to RSS so it's in order beforehand)
    # TODO: Finish commenting (as of 2025 08 04 12:40pm)

    if bool_prints: # Print all data
        for event in events_future:
            print(f"{str_prefix_info} ---------------")
            print("Title:" + " " + event['title'])
            # print("\t Image:" + " " + event['image'])
            print("\t URL:" + " " + event['url'])
            print("\t Date:" + " " + event['date'])
            # print("\t Location (Name):" + " " + event['location_name'])
            print("\t Location (Addr):" + " " + event['location_address'])


    # dummy = input("> ") # ---------------------------------------///////////

    # for entry in reversed(arr_entries):
    #     if not to_rss.check_post_exists(path=rss_path, url=entry['url'], guid=""):
    #         # If the URL is not in the list, add it.
    #         driver.get(entry['url'])# Get the description from the individual page
    #         description = driver.find_element(By.CLASS_NAME, "vcex-post-content-c").text.replace("\n", "\n\n")
    #         entry["description"] = description
    #         # Determine who posted this job posting
    #         # In every posting, the first line is "Posted by ..." followed by "\n"
    #         entry['author'] = entry["title"]
    #         to_rss.add_to_rss(path=rss_path, title=entry['title'], author=entry['author'], date=entry['date'], url=entry['url'], guid="", body=entry['description'])
    #         int_new_postings += 1

    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set

    if bool_prints and int_new_postings>0:
        if int_new_postings == 1:
            print("\t 1 new posting")
        else:
            print(f"\t {int_new_postings} new postings")

    # Exit the program
    sys.exit()


if __name__ == "__main__":
    main()
