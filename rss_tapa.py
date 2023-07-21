'''
rss_tapa.py
Hussein Esmail
Created: 2023 07 08
Updated: 2023 07 20
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

# ========= VARIABLES ===========
bool_run_in_background  = True
bool_prints = True
target_site             = "https://tapa.ca/listing-category/employment-opportunity/"
str_post_description_empty = "null" # The string that appears on posts that haven't been checked for descriptions yet
RSS_POS_INSERT          = "<!-- FEEDS START -->" # Line to insert feed posts
URL_TEMPLATE_RSS        = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss.xml" # Template RSS on my Github that this program relies on
RSS_FOLDER = os.path.expanduser("~/Documents/Local-RSS/TAPA/")
RSS_TITLE = "TAPA Employment Opportunities"
RSS_DESCRIPTION = "TAPA Employment Opportunities"
RSS_FILE_NAME = "tapa.xml"


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

def is_in_list(item, list):
    # This function searches for a substring within every entry of an array
    # Useful for finding if a URL is in a text file at all, when every line of the file is a string in the array
    for list_item in list:
        if item in list_item:
            return True
    return False

def is_internet_connected():
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
        return False
    
def main():
    if not is_internet_connected():
        print(f"{str_prefix_err}You're not connected to the internet!")
        sys.exit(1)

    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Run in background
    os.environ['WDM_LOG'] = str(logging.NOTSET) # Do not output logs for CDM
    cdm = ChromeDriverManager()
    service = Service(cdm.install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.set_window_size(200, 1000) # Window size
    driver.get(target_site)
    lines = []
    int_new_postings = 0

    if not os.path.exists(RSS_FOLDER): # Make dir if it does not exist
        os.makedirs(RSS_FOLDER)
    if os.path.exists(RSS_FOLDER + f"{RSS_FILE_NAME}"):
        # If file exists, read only
        lines = open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'r').readlines()
    else:
        # Make RSS if it does not exist
        urllib.request.urlretrieve(URL_TEMPLATE_RSS, RSS_FOLDER + f"{RSS_FILE_NAME}")
        lines = open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'r').readlines()
        for num, _ in enumerate(lines):
            # Replace info in template
            lines[num] = lines[num].replace("[RSS FEED TITLE]", RSS_TITLE)
            # lines[num] = lines[num].replace("[TERM]", RSS_TERM)
            lines[num] = lines[num].replace("[RSS DESCRIPTION]", RSS_DESCRIPTION)
            # for rep in RSS_LINES_REMOVE:
            #     lines[num] = lines[num].replace('    ' + rep + '\n', "")
        open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'w').writelines(lines)
    
    arr_articles = driver.find_elements(By.XPATH, "/html/body/div/div/main/div/div/div/div[1]/article")
    arr_entries = []
    for article_num in range(len(arr_articles)):
        # print(article.text)
        # test = arr_articles[article_num].find_element(By.XPATH, "//*/h2/a").text
        test = arr_articles[article_num].find_element(By.CLASS_NAME, "wpex-inherit-color-important").text.replace("Employment Opportunity: ", "")
        url = arr_articles[article_num].find_element(By.CLASS_NAME, "wpex-inherit-color-important").get_attribute('href')
        date = arr_articles[article_num].find_element(By.CLASS_NAME, "wpex-card-date").text.replace("Published ", "")
        arr_entries.append({
            "title": test,
            "url": url,
            "date": date,
            "description": str_post_description_empty
        })


        # TODO: Check the number of posts there are until a title matches one that is already in the RSS file

    for entry_num in range(len(arr_entries)):
        # Check descriptions, if it doesn't already have one
        if arr_entries[entry_num]["description"] == str_post_description_empty:
            driver.get(arr_entries[entry_num]["url"])
            description = driver.find_element(By.CLASS_NAME, "vcex-post-content-c").text.replace("\n", "\n\n")
            
            # Replace strings that need to be replaced:
            description = description.replace("&", "&amp;") # Must be before intentional additions of "&" symbols
            description = "&lt;p&gt;" + description # Start the first "<p>" element
            description = description.replace("&#13;", "")
            description = description.replace("'", "&apos;")
            description = description.replace('"', "&quot;")
            description = description.replace("<", "&lt;")
            description = description.replace(">", "&gt;")
            description = description.replace("\n", "&lt;/p&gt; &lt;p&gt;") # "</p> <p>"
            description = description + "&lt;/p&gt;" # End the last "</p>" element

            arr_entries[entry_num]["description"] = description
    
    lines_new = [] # All new lines will be put here before going into the RSS file
    for entry_num in range(len(arr_entries)):
        entry = arr_entries[entry_num]
        url_html = entry["url"]
        if not is_in_list(url_html, lines):
            int_new_postings += 1
            # Determine who posted this job posting
            # In every posting, the first line is "Posted by ..." followed by "\n"
            username = entry["description"].replace("Posted by ", "")[:entry["description"].index("&lt;/p&gt;")].replace("&lt;/p&gt;", "").replace("&lt;p&gt;", "")
            # TODO: PLACEHOLDERS
            entry['time_formatted'] = ""
            # Convert to RSS/XML Format
            lines_new.append(f"<entry>")
            lines_new.append(f"<title>{entry['title']}</title>")
            lines_new.append(f"<published>{entry['time_formatted']}</published>") # Ex. 2021-07-28T20:57:31Z
            lines_new.append(f"<updated>{entry['time_formatted']}</updated>")
            lines_new.append(f"<link href=\"{url_html}\"/>") # Original RSS uses entry.links[0]['href']. .id is neater, and title doesn't need to be in link
            # Adding author of post
            lines_new.append(f"<author>")
            lines_new.append(f"<name>{username}</name>")
            lines_new.append(f"</author>")
            # lines_new.append(f"<category term=\"{RSS_TERM}\" label=\"{RSS_TITLE}\"/>")
            lines_new.append(f"<content type=\"html\">")
            lines_new.append(entry['description'].replace("\n", "<br>")) # Adding HTML description to RSS
            lines_new.append(f"</content>")
            lines_new.append(f"</entry>") # End of RSS post

    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set
    # Write new lines to RSS file
    lines_new = [line + "\n" for line in lines_new] # Done for formatting
    rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT) # Find the RSS Delimiter out of the stripped version of the array (each line stripped)
    lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array at the RSS delimiter position
    open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'w').writelines(lines) # Replace previous RSS lines
    
    if bool_prints:
        if int_new_postings == 1:
            print("\t 1 new posting")
        else:
            print(f"\t {int_new_postings} new postings")
    
    # Exit the program
    sys.exit() 
    

if __name__ == "__main__":
    main()
