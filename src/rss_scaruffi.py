'''
rss_scaruffi.py
Hussein Esmail
Created: 2022 05 31
Updated: 2022 05 31
Description: [DESCRIPTION]
'''

import os
import re
import sys # To exit the program
from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.support.ui import Select  # Used to select from drop down menus
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)
# from selenium.webdriver.common.keys import Keys  # Used for pressing special keys, like 'enter'

# ========= VARIABLES ===========
RSS_FOLDER              = os.path.expanduser("~/.config/rss-parsers/")
RSS_FILENAME            = "scaruffi1.xml" # Output file name
RSS_POS_INSERT          = "<!-- FEEDS START -->" # Line to insert feed posts
bool_run_in_background  = True
target_site             = "https://scaruffi.com/" # Site to get content from
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

def main():
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    service = Service(ChromeDriverManager(log_level=0).install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(200, 1000) # Window size
    driver.get(target_site)

    list_all    = driver.find_elements(By.XPATH, "/html/body/center/table[2]/tbody/tr/td[3]/font[2]")[0]
    list_titles = driver.find_elements(By.XPATH, "/html/body/center/table[2]/tbody/tr/td[3]/font[2]")[0].find_elements(By.XPATH, ".//font")
    list_posts  = driver.find_elements(By.XPATH, "/html/body/center/table[2]/tbody/tr/td[3]/font[2]")[0].find_elements(By.XPATH, ".//a")

    # List of HTML elements as text in an array
    list_elem_text = list_all.get_attribute('innerHTML').split("\n")

    posts = [] # Array of dictionaries

    # Getting all the titles
    for elem in list_elem_text:
        if "font" in elem:
            try:
                test = re.search("<br><font color=\"green\">(.+?)</font>:", elem).group(1).strip()
                posts.append({"category": test})
                # print(test)
            except:
                # print(elem)
                pass

    # print(f"Titles: {len(posts)}")
    url_num = 0 # URL counter
    for num, elem in enumerate(list_elem_text):
        # print("NUM: ", num)
        if "href" in elem:
            url_split = elem.split("\"")
            if url_num < len(posts):
                posts[url_num]["url"] = url_split[1] # URL
                # posts[url_num]["title"] = "\"".join(url_split[4:-1]).replace("&amp;", "&") # Title
                posts[url_num]["title"] = elem.split(">")[-2].split("</a")[0]
                if posts[url_num]["title"].count("\"") % 2 == 1:
                    posts[url_num]["title"] = posts[url_num]["title"] + "\""
                if posts[url_num]["url"][0:4] != "http":
                    posts[url_num]["url"] = target_site + posts[url_num]["url"]
                url_num += 1 # Increment counter for next post

    # At this point, we have the data that we can add to the RSS feed
    for item in posts:
        # Print the data
        print(f"[{item['category']}] {item['title']}: {item['url']}")

    # Check if the RSS file exists. Otherwise, create it. Then we can add stuff
    if not os.path.exists(RSS_FOLDER): # Make dir if it does not exist
        os.makedirs(RSS_FOLDER)
    if os.path.exists(RSS_FOLDER + RSS_FILENAME):
        # If file exists, read only
        lines = open(RSS_FOLDER + RSS_FILENAME, 'r').readlines()
    else:
        # Make RSS if it does not exist
        urllib.request.urlretrieve(URL_TEMPLATE_RSS, RSS_FOLDER + RSS_FILENAME)
        lines = open(RSS_FOLDER + RSS_FILENAME, 'r').readlines()
        for num, _ in enumerate(lines):
            # Replace info in template
            lines[num] = lines[num].replace("[RSS FEED TITLE]", RSS_TITLE).replace("[TERM]", RSS_TERM).replace("[RSS DESCRIPTION]", RSS_DESCRIPTION)
            for rep in RSS_LINES_REMOVE:
                lines[num] = lines[num].replace('    ' + rep + '\n', "")
        open(RSS_FOLDER + RSS_FILENAME, 'w').writelines(lines)
            # Replace template lines with filled in info

    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set
    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
