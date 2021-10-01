'''
rss_tiktok.py
Hussein Esmail
Created: 2021 09 22
Updated: 2021 09 22
Description: This program gets the most recent TikTok video URLs from a user then adds it to an RSS file at the chosen desktop location.
'''

import os
import sys # To exit the program
from selenium import webdriver
from selenium.common.exceptions import *
# from selenium.webdriver.support.ui import Select  # Used to select from drop down menus
from selenium.webdriver.chrome.options import Options  # Used to add aditional settings (ex. run in background)
import platform
import datetime
import requests                 # Used to get HTML
import urllib                   # Used to copy template RSS file from my Github

# == User-configurable variables
RSS_FOLDER = os.path.expanduser("~/Documents/Local-RSS/Tiktok/")
RSS_TERM = "TikTok"
RSS_DESCRIPTION = "Tiktok recent videos"
BOOL_QUIET = False               # Quiet mode
TIKTOK_URLS = os.path.expanduser("~/Documents/Local-RSS/Tiktok/urls")

# == Other global variables
RSS_LINES_REMOVE = ['<!-- <icon></icon> -->', '<!-- <id></id> -->', '<!-- <logo></logo> -->', '<link rel="self" href="[LINK TO THIS RSS]" type="application/atom+xml" />', '<link rel="alternate" href="[LINK ALTERNATE]" type="text/html" />']
RSS_POS_INSERT = "<!-- FEEDS START -->"                                 # Used for RSS feed posts - Where to insert after
URL_RSS = "https://yfile.news.yorku.ca/feed/atom/"                      # YFile RSS URL
URL_TEMPLATE_RSS = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss.xml" # Template RSS on my Github that this program relies on


bool_use_Brave = False
bool_run_in_background = False
os_type = platform.platform().split("-")[0]
path_urls = os.path.expanduser("~/Documents/Local-RSS/TikTok/urls")
if os_type == "Linux":
    chromedriver_path = os.path.expanduser("~/Documents/Coding/py/reference/Chromedriver/chromedriver")
elif os_type == "macOS":
    chromedriver_path = "/Users/hussein/Documents/Coding/py/reference/Chromedriver/chromedriver"


def is_in_list(item, list):
    for list_item in list:
        if item in list_item:
            return True
    return False

def main():
    usernames = open(TIKTOK_URLS, 'r').readlines()
    usernames = [username.replace('\n', '') for username in usernames]
    feed_counter = 0
    for username in usernames:
        new_videos = 0
        feed_counter += 1
        RSS_FILENAME = f"{username}.xml"
        RSS_TITLE = username
        target_site = f"https://www.tiktok.com/@{username}"
        # if not BOOL_QUIET:
        #     print(f"User: {target_site}")
        #     print(f"RSS folder location: {RSS_FOLDER}")
        lines_new = []
        vid_links = [] 
        options = Options()  
        if bool_run_in_background:
            options.add_argument("--headless")  # Adds the argument that hides the window
        if bool_use_Brave:
            options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
            driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome(chromedriver_path, options=options)
        driver.get(target_site)
        temp = driver.find_elements_by_class_name("video-feed-item-wrapper")
        # print(len(temp))
        for i in temp:
            vid_links.append(i.get_attribute('href')) # Video links

        # print("\n".join(vid_links))
        # Cleanup
        driver.close()  # Close the browser
        options.extensions.clear() # Clear the options that were set
        
        if not os.path.exists(RSS_FOLDER):                              # Make dir if it does not exist
            os.makedirs(RSS_FOLDER)
            # if not BOOL_QUIET:
            #     print(f"Made dir: {RSS_FOLDER}")
        if os.path.exists(RSS_FOLDER + RSS_FILENAME):                   # If RSS fole exists, read it only  
            # if not BOOL_QUIET:        
            #     print(f"Read RSS file: {RSS_FILENAME}")   
            lines = open(RSS_FOLDER + RSS_FILENAME, 'r').readlines()
        else:                                                           # Make RSS if it does not exist
            urllib.request.urlretrieve(URL_TEMPLATE_RSS, RSS_FOLDER + RSS_FILENAME)
            lines = open(RSS_FOLDER + RSS_FILENAME, 'r').readlines()
            for num, _ in enumerate(lines):                             # Replace info in template
                lines[num] = lines[num].replace("[RSS FEED TITLE]", RSS_TITLE).replace("[TERM]", RSS_TERM).replace("[RSS DESCRIPTION]", RSS_DESCRIPTION)
                for rep in RSS_LINES_REMOVE:
                    lines[num] = lines[num].replace('    ' + rep + '\n', "")
            open(RSS_FOLDER + RSS_FILENAME, 'w').writelines(lines)      # Replace template lines with filled in info
            # if not BOOL_QUIET:
            #     print(f"Created RSS file: {RSS_FILENAME}")   
        # if not BOOL_QUIET:
        #     print(f"Videos found: {len(vid_links)}")
        for url in vid_links:
            if not is_in_list(url, lines):
                new_videos += 1
                content_desc = f"\t\t<a href='{url}'>Tiktok Video URL</a>"
                content_desc = content_desc.replace("\n", "")
                content_desc = content_desc.replace("\t", "")
                content_desc = content_desc.replace("&#13;", "")        # :before and :after (not needed)
                content_desc = content_desc.replace("&", "&amp;")       # Replace HTML elements in RSS description
                content_desc = content_desc.replace("'", "&apos;")  
                content_desc = content_desc.replace('"', "&quot;")
                content_desc = content_desc.replace("<", "&lt;")
                content_desc = content_desc.replace(">", "&gt;")
                lines_new.append(f"\t<entry>")
                lines_new.append(f"\t\t<title>{RSS_TITLE}</title>")
                lines_new.append(f"\t\t<published>{datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()}</published>") # Ex. 2021-07-28T20:57:31Z
                lines_new.append(f"\t\t<updated>{datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()}</updated>")
                lines_new.append(f"\t\t<link href=\"{url}\"/>")    # Original RSS uses entry.links[0]['href']. .id is neater, and title doesn't need to be in link
                lines_new.append(f"\t\t<author>")
                lines_new.append(f"\t\t\t<name>@{username}</name>")
                lines_new.append(f"\t\t</author>")
                lines_new.append(f"\t\t<category term=\"{RSS_TERM}\" label=\"{RSS_TITLE}\"/>")
                lines_new.append(f"\t\t<content type=\"html\">")
                lines_new.append(content_desc)
                lines_new.append(f"\t\t</content>")
                lines_new.append(f"\t</entry>")
                # if not BOOL_QUIET:
                #     print(f"[\033[92mDONE\033[0m] {url}")
                
        lines_new = [line + "\n" for line in lines_new]                 # Done for formatting
        rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT)
        lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array
        open(RSS_FOLDER + RSS_FILENAME, 'w').writelines(lines)          # Replace previous RSS lines
        if not BOOL_QUIET:
            print(f"[\033[92mDONE\033[0m] {feed_counter}/{len(usernames)}: {new_videos} new from @{username}")

    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
