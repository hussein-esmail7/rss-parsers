'''
rss_tapa.py
Hussein Esmail
Created: 2023 07 08
Updated: 2023 07 22
Description: RSS Parser for TAPA (Toronto Alliance for the Performing Arts) Employment Opportunity Listings
'''

import os
import sys # To exit the program
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
bool_run_in_background  = True
bool_prints = True
target_site             = "https://tapa.ca/listing-category/employment-opportunity/"
RSS_TITLE = "TAPA Employment Opportunities"
RSS_DESCRIPTION = "TAPA Employment Opportunities"


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
    rss_path = "~/.config/rss-parsers/TAPA/tapa.xml"
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
    
    arr_articles = driver.find_elements(By.XPATH, "/html/body/div/div/main/div/div/div/div[1]/article")
    arr_entries = []
    for article in arr_articles:
        title = article.find_element(By.CLASS_NAME, "wpex-inherit-color-important").text.replace("Employment Opportunity: ", "").replace("Job Opportunity: ", "")
        url = article.find_element(By.CLASS_NAME, "wpex-inherit-color-important").get_attribute('href')
        date = article.find_element(By.CLASS_NAME, "wpex-card-date").text.replace("Published ", "")
        arr_entries.append({
            "title": title,
            "url": url,
            "date": get_past_date(date),
            "author": "",
            "description": ""
        })

    for entry in reversed(arr_entries):
        if not to_rss.check_post_exists(path=rss_path, url=entry['url'], guid=""):
            # If the URL is not in the list, add it. 
            driver.get(entry['url'])# Get the description from the individual page
            description = driver.find_element(By.CLASS_NAME, "vcex-post-content-c").text.replace("\n", "\n\n")
            entry["description"] = description
            # Determine who posted this job posting
            # In every posting, the first line is "Posted by ..." followed by "\n"
            entry['author'] = entry["title"]
            to_rss.add_to_rss(path=rss_path, title=entry['title'], author=entry['author'], date=entry['date'], url=entry['url'], guid="", body=entry['description'])
            int_new_postings += 1

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
