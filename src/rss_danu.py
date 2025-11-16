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
# from bs4 import BeautifulSoup, Tag, NavigableString
# import requests
import datetime
import json
import logging
import feedparser # Used to import existing RSS feeds
from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import Select  # Used to select from drop down menus
from dateutil.relativedelta import relativedelta
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)
# from selenium.webdriver.common.keys import Keys  # Used for pressing special keys, like 'enter'
import to_rss # Python function file in same directory
from feedgen.feed import FeedGenerator

# ========= VARIABLES ===========
bool_run_in_background  = True
bool_prints             = True
bool_prints_bulk        = False
author = "Danu Social House"
target_site             = "https://www.danusocialhouse.ca/events"
RSS_TITLE = "Danu Social House"
RSS_DESCRIPTION = "Unofficial feed hosted and maintained (when I can) by Hussein Esmail"
desc_footer = "\n\nDanu Social House\n(416) 535-4144\nevents@danu.house\n\n1237 Queen St W\nToronto, ON M6K 1L4"

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
    rss_path = "~/.config/rss-parsers/danusocialhouse/danusocialhouse.xml"
    int_new_postings = 0
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Run in background
    os.environ['WDM_LOG'] = str(logging.NOTSET) # Do not output logs for CDM
    service = Service()
    driver = webdriver.Chrome()
    driver.get(target_site)
    driver.implicitly_wait(0.5)
    to_rss.create_rss(path=rss_path, title=RSS_TITLE, subtitle=RSS_DESCRIPTION)

    events_list = driver.find_elements(By.CLASS_NAME, 'event-collection-item')
    if bool_prints:
        print(f"{str_prefix_info} # of event list items: {len(events_list)}")

    parsed_items = []
    for event in events_list:
        event_url = event.find_element(By.TAG_NAME, 'a').get_attribute('href')
        event_title = event.find_element(By.CLASS_NAME, 'event-card-title').text
        event_timeinfo = event.find_element(By.CLASS_NAME, 'event-card-datetime')
        event_date = event_timeinfo.find_element(By.CLASS_NAME, 'event-date').text
        event_times = event_timeinfo.find_elements(By.CLASS_NAME, 'event-time')

        # Get start time and convert to datetime format
        event_time_start = event_times[0].text # Ex. "7:00 pm"
        yr = datetime.datetime.now().year # year
        mo = time.strptime(event_date.split(' ')[0],'%b').tm_mon # month as number
        da = int(event_date.split(' ')[-1]) # day as number
        hr = int(event_time_start.split(":")[0].strip()) # hour as number - All characters up to ":"
        mi = int(event_time_start.split(":")[1][0:1].strip()) # minute as number - First 2 characters after ":"
        if "pm" in event_time_start.lower(): # hour to 24hr format
            hr += 12
        # TODO: Set Toronto time Zone
        event_time_start = datetime.datetime(year=yr, month=mo, day=da, hour=hr, minute=mi, tzinfo=None)

        # Get start end and convert to datetime format
        event_time_end = event_times[-1].text # Ex. "10:00 pm"
        # Hour and minute are the only things that change
        hr = int(event_time_end.split(":")[0].strip()) # hour as number - All characters up to ":"
        mi = int(event_time_end.split(":")[1][0:1].strip()) # minute as number - First 2 characters after ":"
        if "pm" in event_time_end.lower(): # hour to 24hr format
            hr += 12
        # TODO: Set Toronto time Zone
        event_time_end = datetime.datetime(year=yr, month=mo, day=da, hour=hr, minute=mi, tzinfo=None)
        
        if event_time_start > event_time_end: 
            # If the end time is before the start time, it is likely the event ends after midnight
            # Move the end time to the next day
            event_time_end += relativedelta(days=1)
        
        # If the current date is newer than the date in question by more than 3 months, move it to the next year
        # 3 months in case an event just happened
        longago = datetime.datetime.now() - relativedelta(months=3)
        if event_time_start < longago:
            event_time_start = event_time_start + relativedelta(years=1)
            event_time_end = event_time_end + relativedelta(years=1)

        parsed_items.append({
            'url': event_url,
            'title': event_title,
            'time_start': event_time_start,
            'time_end': event_time_end,
            'description': "",
            'uuid': event_time_start.isoformat() + " " + event_title,
            'published': datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT") # 'Thu, 05 Sep 2002 00:00:01 GMT' format
            })
        
    if bool_prints:
        print(f"{str_prefix_info} Found {len(parsed_items)} items")

    for item in parsed_items:
        # Create description of each post
        driver.get(item['url'])
        time.sleep(0.3)

        # print(str(driver.find_element(By.CLASS_NAME, "event-paragraph-rich-text").text))
        # dummy = input("> ")

        item['description'] =  item['time_start'].strftime("%B %d, %Y %I:%M%p")
        item['description'] += " to "
        item['description'] += item['time_end'].strftime("%I:%M%p")
        item['description'] += "\n\n"
        item['description'] += driver.find_element(By.CLASS_NAME, "event-paragraph-rich-text").text 
        item['description'] += desc_footer
        item['description'] += "\n\n"
        
    # Save as JSON
    # Construct filename
    timestamp = datetime.datetime.now().isoformat(timespec='seconds').replace(":", "-")
    filename = f"data_{timestamp}_danu.json"
    # Convert all datetime objects to str (ISO format), or else json parser crashes
    for item in parsed_items:
        item['time_start'] = item['time_start'].isoformat()
        item['time_end'] = item['time_end'].isoformat()
    # Export dictionary as JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(parsed_items, f, indent=4, ensure_ascii=False)
    if bool_prints:
        print(f"{str_prefix_info} Saved JSON file {filename}")

    # Print raw data 
    if bool_prints_bulk:
        for item in parsed_items:
            print(f"{str_prefix_info} {item['title']}")
            print(f"\t{item['time_start'][:item['time_start'].index('T')]} at {item['time_start'][item['time_start'].index('T'):]} to {item['time_end'][item['time_end'].index('T'):]}")
            # print(f"\t{item['time_start']} to {item['time_end']}")
            print(f"\t\t{item['description']}")
            print(f"\tSee {item['url']}")
    
    # print("\n")
    # dummy = input("> ")
    
    # Cleanup
    driver.close()  # Close the browser, no longer needed for the rest of the program

    fg = FeedGenerator()
    fg.id('https://www.danusocialhouse.ca/events') # TODO: Verify if this is supposed to be the source URL or the URL to the feed itself
    fg.title(RSS_TITLE)
    fg.author( {'name':'Hussein Esmail','email':'HusseinEsmailContact@gmail.com'} )
    fg.link( href='https://www.danusocialhouse.ca/events', rel='alternate')
    # fg.logo('http://ex.com/logo.jpg')
    fg.subtitle(RSS_DESCRIPTION)
    fg.link(href='https://husseinesmail.xyz/rss/danusocialhouse.xml', rel='self') # TODO: Link to self
    fg.language('en')

    if os.path.exists(rss_path):
        # If the feed already exists, parse all existing items into the new feed
        # first so that they carry over and don't get overwritten
        d = feedparser.parse(rss_path)
        for element in enumerate(d.entries):
            parsed_items.append({
                'url': element.link,
                'title': element.title,
                'time_start': event_time_start,
                'time_end': event_time_end,
                'description': element.description,
                'uuid': element.id,
                'published': element.published # 'Thu, 05 Sep 2002 00:00:01 GMT' format
            })
            # 0 = most recent
            # 1 = 2nd recent
            # ...
            # -1 = earliest
    else:
        

    for entry in reversed(parsed_items):
        # Reversed = oldest first since the webpage is newest to oldest, but we want oldest to newest
        if not to_rss.check_post_exists_guid(path=rss_path, guid=entry['uuid']):
            # If the post is not in the list, add it.
            to_rss.add_to_rss(path=rss_path, title=entry['title'], author=author, date=datetime.datetime.now().isoformat(), url=entry['url'], guid=entry['uuid'], body=entry['description'], use_cdata=False)
            # Source - https://stackoverflow.com/a/77706593
            fe = fg.add_entry()
            fe.id(entry['uuid'])
            fe.title(entry['title'])
            fe.link(href=entry['url'])
            fe.description(entry['description'])
            fe.published(entry['published'])
            int_new_postings += 1

    rssfeed = fg.rss_str(pretty=True) # Get the RSS feed as string
    fg.rss_file(rss_path) # Write the RSS feed to a file

    if bool_prints:
        print(rssfeed)
        print("\n\n")

    if bool_prints and int_new_postings>0:
        if int_new_postings == 1:
            print("\t 1 new posting")
        else:
            print(f"\t {int_new_postings} new postings")

    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
