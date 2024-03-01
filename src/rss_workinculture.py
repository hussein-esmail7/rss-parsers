'''
rss_workinculture.py
Hussein Esmail
Created: 2023 05 06
Updated: 2024 03 01
Description: This program gets job postings from an existing Work In Culture 
    RSS feed because the RSS feed they give contains nothing except the actual 
    URL to the posting.
'''

# Next steps:
# - TODO: Redo entire program (site was redesigned since last edit). Currently 
#           in progress but the final RSS feed generation is untested due to 
#           slow internet connection
# - TODO: Convert RSS file to RSS 2.0 (refer to rss_citt.py)
# - TODO: Each page is normally 10 entries long. This program only looks at the 
#           first (newest) page. If none of the entries were in the file 
#           beforehand (are all new), it's possible the 11th on the second page 
#           is also new. By the end of the loop, if a duplicate entry is not 
#           found, scan the next page (and the next, and the next, ...)
# - TODO: Program doesn't use the URLs file. At the moment, the search URL is hardcoded

import dateutil.parser as parser # Used to convert date to RSS ISO format
import logging # Used to turn off chromedriver logs
import os
import sys # To exit the program
import urllib.request # To check internet connection and download urls
import re
from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)

# Libraries addd 2024 03 01
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

# ========= VARIABLES ===========
RSS_FOLDER              = os.path.expanduser("~/.config/rss-parsers/WorkInCulture/")
RSS_TERM                = "WorkInCulture"
RSS_POS_INSERT          = "<!-- FEEDS START -->" # Line to insert feed posts
URL_TEMPLATE_RSS        = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss.xml" # Template RSS on my Github that this program relies on
bool_run_in_background  = False # TODO: Temporary
RSS_FILE_NAME = "workinculture_test.xml"
RSS_TITLE = "WorkInCulture Job Postings"
RSS_DESCRIPTION = "WorkInCulture Job Postings"
bool_prints = True

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
str_prefix_warn         = f"[{color_yellow}WARN{color_end}]\t "
str_prefix_indent       = f"[{color_red}>>>>{color_end}]\t "

def is_in_list(item, list):
    # This function searches for a substring within every entry of an array
    # Useful for finding if a URL is in a text file at all, when every line 
    # of the file is a string in the array
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
    int_new_postings = 0
    url = "https://workinculture.ca/job-search/#q=&type-of-listing=paid-employment"
    arr_postings = []
    delay = 10 # Maximum timeout in seconds when initially loading the page with all the listings

    if not is_internet_connected():
        print(f"{str_prefix_err}You're not connected to the internet!")
        sys.exit(1)
    print("\tLoading...")
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Run in background
    os.environ['WDM_LOG'] = str(logging.NOTSET) # Do not output logs for CDM
    cdm = ChromeDriverManager()
    service = Service(cdm.install())
    driver = webdriver.Chrome(service=service, options=options)
    BOOL_PRINTS = True # True = allow prints. False = no output whatsoever
    if is_in_list("-q", sys.argv) or is_in_list("--quiet", sys.argv):
        BOOL_PRINTS = False
    
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

    driver.get(url)

    # Load JavaScript elements list of job positings
    try:
        _ = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/main/div[1]/div/div/div[3]/div/div/div[1]/div/ol/li')))
        # print("Page is ready!")
    except TimeoutException:
        print(f"{str_prefix_err} Loading webpage took longer than {delay}s. Exiting...")
        sys.exit(1)
    
    job_list_elements = driver.find_elements(By.XPATH, '/html/body/div/main/div[1]/div/div/div[3]/div/div/div[1]/div/ol/li') # The ordered list that contains list elements (one per job post)
    print(f"Number of rows (job postings): {len(job_list_elements)}")
    
    bool_continue_searching = True
    for list_item_num, list_item in enumerate(job_list_elements):
        # If it couldn't get the last element, don't get the next one (aka end the for loop early)
        if bool_continue_searching:
            # Wait for this specific list_item to load (list may be too long for it to all load at the beginning)
            # Locates the title element of the element
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Scroll to bottom of webpage
                _ = WebDriverWait(list_item, delay).until(EC.presence_of_element_located((By.XPATH, ".//article/a/div[2]/h4")))
                # print("Page is ready!")
            except TimeoutException:
                print(f"{str_prefix_err} Post {list_item_num+1} of {len(job_list_elements)} took longer than {delay}s to load.")
                print(f"{str_prefix_warn} Only treating top {list_item_num} postings.")
                bool_continue_searching = False
            # This if statement is here twice because if this one isn't here, it will still try to get info from the element 
            # it wasn't able to locate in the last try/except statement
            if bool_continue_searching:
                # The deadline 'p' element contains a "strong" element that just has "Closes: " which isn't needed.
                try:
                    text_deadline_temp = list_item.find_element(By.CLASS_NAME, "closes")
                    text_deadline_temp2 = text_deadline_temp.find_element(By.TAG_NAME, "strong").text
                    text_deadline_temp = text_deadline_temp.text.replace(text_deadline_temp2, "").strip()
                except NoSuchElementException:
                    text_deadline_temp = f"{str_prefix_err} N/A"
                # The location 'p' element contains a "strong" element that just has "Location: " which isn't needed.
                try:
                    text_location_temp = list_item.find_element(By.CLASS_NAME, "location")
                    text_location_temp2 = text_location_temp.find_element(By.TAG_NAME, "strong").text
                    text_location_temp = text_location_temp.text.replace(text_location_temp2, "").strip()
                except NoSuchElementException:
                    text_location_temp = f"{str_prefix_err} N/A"
                # The date posted 'p' element contains a "strong" element that just has "Posted: " which isn't needed.
                try:
                    text_posted_temp = list_item.find_element(By.CLASS_NAME, "hit_posted_on")
                    text_posted_temp2 = text_posted_temp.find_element(By.TAG_NAME, "strong").text
                    text_posted_temp = text_posted_temp.text.replace(text_posted_temp2, "").strip()
                except NoSuchElementException:
                    text_posted_temp = f"{str_prefix_err} N/A"
                arr_postings.append({
                    'title': list_item.find_element(By.XPATH, ".//article/a/div[2]/h4").text, # TODO
                    'url': list_item.find_element(By.XPATH, ".//article/a").get_attribute("href"),
                    'organization': f"{str_prefix_err} N/A", # TODO
                    'city': text_location_temp,
                    'type': f"{str_prefix_err} N/A", # TODO: Part time or full time
                    'deadline': text_deadline_temp, # Format: "Sep 01, 2023"
                    'date': text_posted_temp, # Format: "Sep 01, 2023"
                    'description': f"{str_prefix_err} N/A", # To be filled if the entry doesn't exist in the RSS file,
                    'guid': f"{str_prefix_err} N/A" # Used to prevent saving duplicates in RSS file
                })
                arr_postings[-1]['guid'] = re.sub("^\w+", "", arr_postings[-1]['title']+arr_postings[-1]['date']+arr_postings[-1]['url'])
                # print("="*30)
                # print(" "*4 + f"Title: {arr_postings[-1]['title']}")
                # print(" "*4 + f"URL: {arr_postings[-1]['url']}")
                # # print(" "*4 + f"Company: {arr_postings[-1]['organization']}")
                # print(" "*4 + f"Location: {arr_postings[-1]['city']}")
                # # print(" "*4 + f"PT/FT: {arr_postings[-1]['type']}")
                # print(" "*4 + f"Deadline: {arr_postings[-1]['deadline']}")
                # print(" "*4 + f"Posted: {arr_postings[-1]['date']}")
                # # print(" "*4 + f"Description: {arr_postings[-1]['description']}")
                print(f"GUID: {arr_postings[-1]['guid']}")
    # From this point onwards: Make the RSS posts of the job listings it was able to get

    lines_new = [] # All new lines will be put here before going into the RSS file
    bool_is_post_not_in_file = True 
    for post_num, posting in enumerate(arr_postings):
        # Check if the current post is already in the RSS file
        with open(RSS_FOLDER + f"{RSS_FILE_NAME}") as myfile:
            if posting['guid'] in myfile.read():
                bool_is_post_not_in_file = False # Post is already in RSS file, do not add
        # print(bool(is_in_list(posting['guid'], lines)))
        if bool_is_post_not_in_file:
            # If the URL is not in the list, add it. 
            int_new_postings += 1
            driver.get(posting['url']) # Get the description (here because we only want to do new posts because it costs time)
            # adElement = driver.find_element(By.CLASS_NAME, 'posting-details').get_attribute('innerHTML')
            ad_description_temp = driver.find_element(By.CLASS_NAME, 'single_job_listing').text
            print(ad_description_temp)
            # ad_description_temp = ad_description_temp.replace("Back to the Job Board", "")
            # ad_description_temp = ad_description_temp.replace("LinkedIn Tweet Facebook Email", "")
            # ad_description_temp = ad_description_temp.replace("\n", "\n\n")
            # # ad_description_temp = ad_description_temp[ad_description_temp.index("LinkedIn Tweet Facebook Email"):]
            # # ad_description_temp = ad_description_temp.replace("\n\n\n", "\n")
            # ad_description_temp = ad_description_temp.strip()
            # # ad_description_temp = f"Position Type: {posting['type']}\nApplication Deadline: {posting['deadline']}\nCity: {posting['city']}\n\n" + ad_description_temp
            # ad_description_temp = ad_description_temp.replace("&", "&amp;") # Must be before intentional additions of "&" symbols
            # ad_description_temp = "&lt;p&gt;" + ad_description_temp # Start the first "<p>" element
            # ad_description_temp = ad_description_temp.replace("&#13;", "")
            # ad_description_temp = ad_description_temp.replace("'", "&apos;")
            # ad_description_temp = ad_description_temp.replace('"', "&quot;")
            # ad_description_temp = ad_description_temp.replace("<", "&lt;")
            # ad_description_temp = ad_description_temp.replace(">", "&gt;")
            # ad_description_temp = ad_description_temp.replace("\n", "&lt;/p&gt; &lt;p&gt;") # "</p> <p>"
            # ad_description_temp = ad_description_temp + "&lt;/p&gt;" # End the last "</p>" element
            arr_postings[post_num]['description'] = ad_description_temp # Must be set to arr_postings[post_num]['description'], not posting['description']
            # Convert to RSS/XML Format
            date = parser.parse(posting['date'])
            posting['date'] = date.isoformat()
            lines_new.append(f"<entry>")
            lines_new.append(f"<title>{posting['title']}</title>")
            lines_new.append(f"<published>{posting['date']}</published>") # Ex. 2021-07-28T20:57:31Z
            lines_new.append(f"<updated>{posting['date']}</updated>")
            lines_new.append(f"<link href=\"{posting['url']}\"/>") # Original RSS uses entry.links[0]['href']. .id is neater, and title doesn't need to be in link
            # Adding author of post
            lines_new.append(f"<author>")
            lines_new.append(f"<name>{posting['organization']}</name>")
            lines_new.append(f"</author>")
            lines_new.append(f"<content type=\"html\">")
            # lines_new.append(posting['description'].replace("\n", "<br>")) # Adding HTML description to RSS
            lines_new.append(posting['description']) # Adding HTML description to RSS
            lines_new.append(f"</content>")
            lines_new.append(f"<guid>{posting['guid']}</guid>")
            lines_new.append(f"</entry>") # End of RSS post

    # Cleanup
    driver.close()  # Close the browser
    options.extensions.clear() # Clear the options that were set
    # Write new lines to RSS file
    lines_new = [line + "\n" for line in lines_new] # Done for formatting
    rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT) # Find the RSS Delimiter out of the stripped version of the array (each line stripped)
    lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array at the RSS delimiter position
    open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'w').writelines(lines) # Replace previous RSS lines

    if bool_prints and int_new_postings>0:
        if int_new_postings == 1:
            print("\t 1 new posting")
        else:
            print(f"\t {int_new_postings} new postings")
    
    # Exit the program
    sys.exit() 

if __name__ == "__main__":
    main()
