'''
rss_vsco.py
Hussein Esmail
Created: 2021 09 30
Updated: 2021 09 30
Description: This program gets the most recent VSCO picture URLs from a user then adds it to an RSS file at the chosen desktop location.
'''

import os
import sys # To exit the program
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Used to add aditional settings (ex. run in background)
import platform
import datetime
import urllib.request
import getpass

bool_use_Brave = False
bool_run_in_background = True
os_type = platform.platform().split("-")[0] # Used to get operating system type
if os_type == "Linux":
    chromedriver_path = os.path.expanduser("~/Documents/Coding/py/reference/Chromedriver/chromedriver")
elif os_type == "macOS":
    chromedriver_path = f"/Users/{getpass.getuser()}/Documents/Coding/py/reference/Chromedriver/chromedriver"

RSS_FOLDER = os.path.expanduser("~/Documents/Local-RSS/VSCO/")
RSS_TERM = "VSCO"
VSCO_URLS = RSS_FOLDER + "urls"
RSS_LINES_REMOVE = ['<!-- <icon></icon> -->', '<!-- <id></id> -->', '<!-- <logo></logo> -->', '<link rel="self" href="[LINK TO THIS RSS]" type="application/atom+xml" />', '<link rel="alternate" href="[LINK ALTERNATE]" type="text/html" />']
RSS_POS_INSERT = "<!-- FEEDS START -->"                                 # Used for RSS feed posts - Where to insert after
URL_RSS = "https://yfile.news.yorku.ca/feed/atom/"                      # YFile RSS URL
URL_TEMPLATE_RSS = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss.xml" # Template RSS on my Github that this program relies on

def is_in_list(item, list):
    for list_item in list:
        if item in list_item:
            return True
    return False

def main():
    usernames = open(VSCO_URLS, 'r').readlines()
    usernames = [username.replace('\n', '') for username in usernames]
    feed_counter = 0
    options = Options()  
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    if bool_use_Brave:
        options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
        driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Chrome(chromedriver_path, options=options)
    for username in usernames:
        site_base = f"https://vsco.co/{username}/"
        target_site = f"{site_base}gallery"
        new_posts = 0
        feed_counter += 1
        urls_images = []
        dict_urls = []
        lines_new = []
        RSS_DESCRIPTION = f"VSCO pictures by @{username}"  # Used for RSS feed posts
        RSS_TITLE = f"VSCO - @{username}"
        
        if not os.path.exists(RSS_FOLDER):                              # Make dir if it does not exist
            os.makedirs(RSS_FOLDER)
        if os.path.exists(RSS_FOLDER + f"{username}.xml"):                   # If RSS fole exists, read it only             
            lines = open(RSS_FOLDER + f"{username}.xml", 'r').readlines()
        else:                                                           # Make RSS if it does not exist
            urllib.request.urlretrieve(URL_TEMPLATE_RSS, RSS_FOLDER + f"{username}.xml")
            lines = open(RSS_FOLDER + f"{username}.xml", 'r').readlines()
            for num, _ in enumerate(lines):                             # Replace info in template
                lines[num] = lines[num].replace("[RSS FEED TITLE]", RSS_TITLE).replace("[TERM]", RSS_TERM).replace("[RSS DESCRIPTION]", RSS_DESCRIPTION)
                for rep in RSS_LINES_REMOVE:
                    lines[num] = lines[num].replace('    ' + rep + '\n', "")
            open(RSS_FOLDER + f"{username}.xml", 'w').writelines(lines)      # Replace template lines with filled in info
        
        
        driver.set_window_size(200, 1000)
        driver.get(target_site)
        urls_all = [item.get_attribute("href") for item in driver.find_elements_by_xpath("//a[@href]")]
        for item in urls_all:
            if f"{site_base}media/" in item:
                urls_images.append(item)
                dict_urls.append({
                    "url_html": item,
                    "url_imgs": [],
                    "time_formatted": "",
                    "desc": ""
                })
        for entry in dict_urls:
            driver.get(entry["url_html"])
            entry["url_imgs"] = [item.get_attribute("src") for item in driver.find_elements_by_xpath("//img[@src]")]
            time_unformatted = driver.find_element_by_xpath('//time/span[1]').text + " /" + driver.find_element_by_xpath('//time/span[2]').text
            time_unformatted = time_unformatted.replace("pm", "PM").replace("am", "AM")
            if len(time_unformatted.split("/")[1].split(":")[0]) == 1:
                time_unformatted = time_unformatted.replace("/", "/0")
            entry["time_formatted"] = datetime.datetime.strptime(time_unformatted, "%B %d, %Y /%H:%M%p").astimezone().replace(microsecond=0).isoformat()
            description_possible = driver.find_elements_by_xpath('//p')
            for item in description_possible:
                if "css-1whdjid-Caption" in item.get_attribute("class") and len(item.text) != 0:
                    entry['desc'] = item.text
            if not is_in_list(entry["url_html"], lines):
                url_html = entry["url_html"]
                new_posts += 1
                content_desc = f"<p>{entry['desc']}</p>"
                content_desc += f"\t\t<p><a href='{target_site}'>Profile</a></p>"
                for img_url in entry["url_imgs"]:
                    content_desc += f"\t\t<p><a href='{img_url}'>VSCO Image URL</a></p>"
                content_desc = content_desc.replace("\n", "")
                content_desc = content_desc.replace("\t", "")
                content_desc = content_desc.replace("&#13;", "")        # :before and :after (not needed)
                content_desc = content_desc.replace("&", "&amp;")       # Replace HTML elements in RSS description
                content_desc = content_desc.replace("'", "&apos;")  
                content_desc = content_desc.replace('"', "&quot;")
                content_desc = content_desc.replace("<", "&lt;")
                content_desc = content_desc.replace(">", "&gt;")
                lines_new.append(f"\t<entry>")
                if len(entry['desc']) > 0:
                    lines_new.append(f"\t\t<title>{entry['desc']}</title>")
                else:
                    lines_new.append(f"\t\t<title>New post by @{username}</title>")
                lines_new.append(f"\t\t<published>{entry['time_formatted']}</published>") # Ex. 2021-07-28T20:57:31Z
                lines_new.append(f"\t\t<updated>{entry['time_formatted']}</updated>")
                lines_new.append(f"\t\t<link href=\"{url_html}\"/>")    # Original RSS uses entry.links[0]['href']. .id is neater, and title doesn't need to be in link
                lines_new.append(f"\t\t<author>")
                lines_new.append(f"\t\t\t<name>@{username}</name>")
                lines_new.append(f"\t\t</author>")
                lines_new.append(f"\t\t<category term=\"{RSS_TERM}\" label=\"{RSS_TITLE}\"/>")
                lines_new.append(f"\t\t<content type=\"html\">")
                lines_new.append(content_desc)
                lines_new.append(f"\t\t</content>")
                lines_new.append(f"\t</entry>")

        lines_new = [line + "\n" for line in lines_new]                 # Done for formatting
        rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT)
        lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array
        open(RSS_FOLDER + f"{username}.xml", 'w').writelines(lines)          # Replace previous RSS lines

    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set
    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
