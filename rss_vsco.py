'''
rss_vsco.py
Hussein Esmail
Created: 2021 09 30
Updated: 2022 01 02
Description: This program gets the most recent VSCO picture URLs from a user
    then adds it to an RSS file at the chosen desktop location.
'''

import datetime
import getpass # Used to get username
import os
import sys # To exit the program
import urllib.request
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service # To set Chrome location
from selenium.webdriver.chrome.options import Options # For "run in background"
from selenium.webdriver.common.by import By # Used to get type to search for

# ========= VARIABLES ===========
RSS_FOLDER              = os.path.expanduser("~/Documents/Local-RSS/VSCO/")
RSS_TERM                = "VSCO"
VSCO_URLS               = RSS_FOLDER + "urls" # Folder location for URLs list
RSS_POS_INSERT          = "<!-- FEEDS START -->" # Line to insert feed posts
URL_TEMPLATE_RSS        = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss.xml" # Template RSS on my Github that this program relies on

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
str_prefix_q            = f"[{color_pink}Q{color_end}]"
str_prefix_y_n          = f"[{color_pink}y/n{color_end}]"
str_prefix_ques         = f"{str_prefix_q}\t "
str_prefix_err          = f"[{color_red}ERROR{color_end}]\t "
str_prefix_done         = f"[{color_green}DONE{color_end}]\t "
str_prefix_info         = f"[{color_cyan}INFO{color_end}]\t "
str_prefix_indent       = f"[{color_red}>>>>{color_end}]\t "

RSS_LINES_REMOVE = [
    '<!-- <icon></icon> -->',
    '<!-- <id></id> -->',
    '<!-- <logo></logo> -->',
    '<link rel="self" href="[LINK TO THIS RSS]" type="application/atom+xml" />',
    '<link rel="alternate" href="[LINK ALTERNATE]" type="text/html" />'
]

def is_in_list(item, list):
    for list_item in list:
        if item in list_item:
            return True
    return False

def main():
    BOOL_PRINTS = True # True = allow prints. False = no output whatsoever
    if is_in_list("-q", sys.argv) or  is_in_list("--quiet", sys.argv):
        BOOL_PRINTS = False
    if not os.path.exists(VSCO_URLS):
        print(f"{str_prefix_err}: {VSCO_URLS} does not exist. Please create the file in this folder and run the program again.")
        sys.exit(1)
    elif BOOL_PRINTS:
        print(f"{str_prefix_info}urls file exists - {VSCO_URLS}")
    url_file_lines = open(VSCO_URLS, 'r').readlines()
    usernames = []
    for line in url_file_lines:
        # This is for processing URLs and removing comments and whitespace
        line_first_word = line.strip().split()
        if len(line_first_word) > 0:
            line_first_word = line_first_word[0] # Get first word (since URLs don't have spaces)
            if line_first_word[0] != "#":
                # If first word in the line is not a comment, treat as username
                usernames.append(line_first_word)
    options = Options()
    options.add_argument("--headless")  # Run in background
    service = Service(ChromeDriverManager(log_level=0).install())
    driver = webdriver.Chrome(service=service, options=options)
    if BOOL_PRINTS:
        print(f"{str_prefix_info}Usernames found in urls file: {len(usernames)}")

    for username in usernames:
        site_base = f"https://vsco.co/{username}/"
        target_site = f"{site_base}gallery"
        urls_images = []
        dict_urls = []
        lines_new = []
        RSS_DESCRIPTION = f"VSCO pictures by @{username}" # For RSS feed posts
        RSS_TITLE = f"VSCO - @{username}"
        if BOOL_PRINTS:
            print(f"{str_prefix_info}User: {username}")

        if not os.path.exists(RSS_FOLDER): # Make dir if it does not exist
            os.makedirs(RSS_FOLDER)
        if os.path.exists(RSS_FOLDER + f"{username}.xml"):
            # If file exists, read only
            lines = open(RSS_FOLDER + f"{username}.xml", 'r').readlines()
        else:
            # Make RSS if it does not exist
            urllib.request.urlretrieve(URL_TEMPLATE_RSS, RSS_FOLDER + f"{username}.xml")
            lines = open(RSS_FOLDER + f"{username}.xml", 'r').readlines()
            for num, _ in enumerate(lines):
                # Replace info in template
                lines[num] = lines[num].replace("[RSS FEED TITLE]", RSS_TITLE).replace("[TERM]", RSS_TERM).replace("[RSS DESCRIPTION]", RSS_DESCRIPTION)
                for rep in RSS_LINES_REMOVE:
                    lines[num] = lines[num].replace('    ' + rep + '\n', "")
            open(RSS_FOLDER + f"{username}.xml", 'w').writelines(lines)
            # Replace template lines with filled in info

        driver.set_window_size(200, 1000)
        driver.get(target_site)
        urls_all = [item.get_attribute("href") for item in driver.find_elements(By.XPATH, "//a[@href]")]
        if BOOL_PRINTS:
            print(f"{str_prefix_indent}\t This page has {len(urls_all)} posts")
        for item in urls_all:
            if f"{site_base}media/" in item:
                urls_images.append(item)
                dict_urls.append({
                    "url_html": item,
                    "url_imgs": [],
                    "time_formatted": "",
                    "desc": ""
                })
        for entry in dict_urls: # For each post URL
            driver.get(entry["url_html"]) # Get HTML of each page
            # Get URL for each image and add "https:" at start of each entry
            for item in driver.find_elements(By.XPATH, "//img[@src]"):
                url_unformatted = item.get_attribute("src")
                if "im.vsco.co" in url_unformatted: # So that the favicon doesn't qualify as well (breaks the program)
                    entry["url_imgs"] = ["https:" + url_unformatted[:url_unformatted.index("?")]]
            # Get the time the post in question is posted
            time_unformatted = driver.find_element(By.XPATH, '//time/span[1]').text + " /" + driver.find_element(By.XPATH, '//time/span[2]').text
            # Convert letter casing to match RSS format
            time_unformatted = time_unformatted.replace("pm", "PM").replace("am", "AM")
            if len(time_unformatted.split("/")[1].split(":")[0]) == 1:
                time_unformatted = time_unformatted.replace("/", "/0")
            # Convert string to datetime object
            entry["time_formatted"] = datetime.datetime.strptime(time_unformatted, "%B %d, %Y /%H:%M%p")
            if "PM" in time_unformatted:
                entry["time_formatted"] = entry["time_formatted"] + datetime.timedelta(hours=12)
            entry["time_formatted"] = entry["time_formatted"].astimezone().replace(microsecond=0).isoformat()
            # Get caption of the post
            description_possible = driver.find_elements(By.XPATH, '//p')
            for item in description_possible:
                if "css-1whdjid-Caption" in item.get_attribute("class") and len(item.text) != 0:
                    entry['desc'] = item.text
            if not is_in_list(entry["url_html"], lines):
                # If post is not in RSS, add it
                # These variables are used for the RSS post
                url_html = entry["url_html"] # URL of the post
                content_desc = f"<p>{entry['desc']}</p>"
                content_desc += f"\t\t<p><a href='{target_site}'>Profile</a></p>"
                # Add each image URL
                for img_url in entry["url_imgs"]:
                    content_desc += f"\t\t<p><a href='{img_url}'>VSCO Image URL</a></p>"
                # Converting HTML text to RSS HTML
                content_desc = content_desc.replace("\n", "")
                content_desc = content_desc.replace("\t", "")
                # ":before" and ":after" (not needed)
                content_desc = content_desc.replace("&#13;", "")
                # Replace HTML elements in RSS description
                content_desc = content_desc.replace("&", "&amp;")
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
                lines_new.append(f"\t\t<link href=\"{url_html}\"/>")# Original RSS uses entry.links[0]['href']. .id is neater, and title doesn't need to be in link
                # Adding author of post
                lines_new.append(f"\t\t<author>")
                lines_new.append(f"\t\t\t<name>@{username}</name>")
                lines_new.append(f"\t\t</author>")

                lines_new.append(f"\t\t<category term=\"{RSS_TERM}\" label=\"{RSS_TITLE}\"/>")
                lines_new.append(f"\t\t<content type=\"html\">")
                lines_new.append(content_desc) # Adding HTML description to RSS
                lines_new.append(f"\t\t</content>")
                lines_new.append(f"\t</entry>") # End of RSS post

        lines_new = [line + "\n" for line in lines_new] # Done for formatting
        rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT)
        lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array
        open(RSS_FOLDER + f"{username}.xml", 'w').writelines(lines) # Replace previous RSS lines

    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set
    sys.exit() # Exit the program

if __name__ == "__main__":
    main() # Run the main method
