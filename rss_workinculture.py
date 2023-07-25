'''
rss_workinculture.py
Hussein Esmail
Created: 2023 05 06
Updated: 2023 07 25
Description: This program gets job postings from an existing Work In Culture 
    RSS feed because the RSS feed they give contains nothing except the actual 
    URL to the posting.
'''

# Next steps:
# - TODO: Each page is normally 10 entries long. This program only looks at the 
#           first (newest) page. If none of the entries were in the file 
#           beforehand (are all new), it's possible the 11th on the second page 
#           is also new. By the end of the loop, if a duplicate entry is not 
#           found, scan the next page (and the next, and the next, ...)

import dateutil.parser as parser
import logging # Used to turn off chromedriver logs
import os
import sys # To exit the program
import urllib.request # To check internet connection and download urls
import os
import sys # To exit the program
from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)

# ========= VARIABLES ===========
RSS_FOLDER              = os.path.expanduser("~/Documents/Local-RSS/WorkInCulture/")
RSS_TERM                = "WorkInCulture"
WIC_URLS                = RSS_FOLDER + "urls" # Folder location for URLs list
RSS_POS_INSERT          = "<!-- FEEDS START -->" # Line to insert feed posts
URL_TEMPLATE_RSS        = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss.xml" # Template RSS on my Github that this program relies on
bool_run_in_background  = True
RSS_FILE_NAME = "workinculture.xml"
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
str_prefix_indent       = f"[{color_red}>>>>{color_end}]\t "

def is_in_list(item, list):
    # This function searches for a substring within every entry of an array
    # Useful for finding if a URL is in a text file at all, when every line 
    # of the file is a string in the array
    for list_item in list:
        if item in list_item:
            return True
    return False

def all_exist_in_one_string(list, *str_searches):
    # This function returns true if there's an element with all of these 
    # strings in the same array entry
    # Used to find out if the specific WorkInCulture entry in question is 
    # already in the RSS file (because the URLs alone can be non-descriptive/reused)
    for list_item in list:
        entry_in_list = True # True until proven otherwise. Reset for each element
        for str_search in enumerate(str_searches):
            if entry_in_list and (str_search[1] not in list_item):
                # str_search[1] because str_search returns: (index, str) as a tuple of 2
                entry_in_list = False
        if entry_in_list:
            # If it made it all the way. If not, the loop repeats for the next 
            # string that will be searched
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
    BOOL_PRINTS = True # True = allow prints. False = no output whatsoever
    if is_in_list("-q", sys.argv) or  is_in_list("--quiet", sys.argv):
        BOOL_PRINTS = False
    if not os.path.exists(WIC_URLS):
        print(f"{str_prefix_err}: {WIC_URLS} does not exist. Please create the file in this folder and run the program again.")
        sys.exit(1)
    # elif BOOL_PRINTS:
    #     print(f"{str_prefix_info}urls file exists - {WIC_URLS}")
    url_file_lines = open(WIC_URLS, 'r').readlines()
    WIC_URLS_LIST = [] # The array of URLs to search the RSS feeds for

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

    for line in url_file_lines:
        # This is for processing URLs and removing comments and whitespace
        line_first_word = line.strip().split()
        if len(line_first_word) > 0:
            line_first_word = line_first_word[0] # Get first word (since URLs don't have spaces)
            if line_first_word[0] != "#":
                # If first word in the line is not a comment, treat as username
                WIC_URLS_LIST.append(line_first_word)

    arr_postings = []
    driver.get("https://www.workinculture.ca/JobBoard.aspx?itemid=&region=Ontario&levelid=&city=&ddfrom=&ddto=&pdfrom=&pdto=")
    
    rows = driver.find_elements(By.XPATH, '/html/body/form/div[4]/div[4]/div[1]/div/div/div[@id="jobResultList" and @class="table-responsive"]/table/tbody/tr')
    for rows_num in range(1, len(rows)):
        arr_postings.append({
            'title': rows[rows_num].find_element(By.XPATH, ".//td[1]/a").text,
            'url': rows[rows_num].find_element(By.XPATH, ".//td[1]/a").get_attribute("href"),
            'organization': rows[rows_num].find_element(By.XPATH, ".//td[1]/p").text,
            'city': rows[rows_num].find_element(By.XPATH, ".//td[2]").text,
            'type': rows[rows_num].find_element(By.XPATH, ".//td[3]").text, # Part time or full time
            'deadline': rows[rows_num].find_element(By.XPATH, ".//td[4]").text, # Format: "Sep 01, 2023"
            'date': rows[rows_num].find_element(By.XPATH, ".//td[5]").text, # Format: "Sep 01, 2023"
            'description': "" # To be filled if the entry doesn't exist in the RSS file
        })

    lines_new = [] # All new lines will be put here before going into the RSS file
    bool_continue_parsing_to_rss = True # Continue until it finds an entry that's already there
    for post_num in range(len(arr_postings)):
        posting = arr_postings[post_num]
        if all_exist_in_one_string(lines, posting['url'], posting['title'], posting['organization']):
            # Checks if the current entry in question is already in the RSS file. 
            # Normally this would just check if the URL in question is in the 
            # file at all using 'is_in_list(url_html, lines)', but for 
            # WorkInCulture, the URLs can be non-descriptive or repetitive, so 
            # I'm looking for the combination of the job title, organization 
            # that posted it, and the URL combined (must all be in the same 
            # line)
            bool_continue_parsing_to_rss = False
        elif bool_continue_parsing_to_rss:
            # If the URL is not in the list, add it. 
            # If bool_continue_parsing_to_rss is False, then don't do any more conversions
            int_new_postings += 1
            driver.get(posting['url'])
            # adElement = driver.find_element(By.CLASS_NAME, 'posting-details').get_attribute('innerHTML')
            adText = driver.find_element(By.CLASS_NAME, 'posting-details').text
            adText = adText.replace("Back to the Job Board", "")
            adText = adText.replace("LinkedIn Tweet Facebook Email", "")
            adText = adText.replace("\n", "\n\n")
            # adtext = adText[adText.index("LinkedIn Tweet Facebook Email"):]
            # adText = adText.replace("\n\n\n", "\n")
            adText = adText.strip()
            # adText = f"Position Type: {posting['type']}\nApplication Deadline: {posting['deadline']}\nCity: {posting['city']}\n\n" + adText
            adText = adText.replace("&", "&amp;") # Must be before intentional additions of "&" symbols
            adText = "&lt;p&gt;" + adText # Start the first "<p>" element
            adText = adText.replace("&#13;", "")
            adText = adText.replace("'", "&apos;")
            adText = adText.replace('"', "&quot;")
            adText = adText.replace("<", "&lt;")
            adText = adText.replace(">", "&gt;")
            adText = adText.replace("\n", "&lt;/p&gt; &lt;p&gt;") # "</p> <p>"
            adText = adText + "&lt;/p&gt;" # End the last "</p>" element
            
            arr_postings[post_num]['description'] = adText # Must be set to arr_postings[post_num]['description'], not posting['description']
            
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
            lines_new.append(posting['description'].replace("\n", "<br>")) # Adding HTML description to RSS
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
