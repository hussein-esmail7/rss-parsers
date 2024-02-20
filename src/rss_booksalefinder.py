'''
rss_booksalefinder.py
Hussein Esmail
Created: 2023 12 09
Updated: 2024 02 20
Description: A program that converts book sale postings to RSS feeds by city 
    (mainly focused on Toronto). Refer to N11-P183.
'''

from selenium import webdriver
import os
import sys # To exit the program
from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)
import datetime
import json
import urllib.request # To download template RSS document
from email.utils import format_datetime # Convert datetime object to RFC822, which RSS 2.0 requires

# ========= VARIABLES ===========
bool_run_in_background  = True # Hide selenium Chrome window
bool_output_to_json = False 
output_directory = os.path.expanduser("~/.config/rss-parsers/Booksalefinder") # Where to put output files
query_cities = ['Toronto'] # Cities that go into the RSS file
RSS_FOLDER   = os.path.expanduser("~/.config/rss-parsers/Booksalefinder/")
RSS_TERM                = "Booksalefinder"
RSS_POS_INSERT          = "<!-- FEEDS START -->" # Line to insert feed posts
URL_TEMPLATE_RSS        = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss2.xml" # Template RSS on my Github that this program relies on
RSS_FILE_NAME           = "booksalefinder.xml"
RSS_TITLE               = f"Booksalefinder for {', '.join(query_cities)}"
RSS_DESCRIPTION         = f"Booksalefinder for {', '.join(query_cities)}"

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
str_prefix_warn         = f"[{color_yellow}WARN{color_end}]\t "
str_prefix_done         = f"[{color_green}DONE{color_end}]\t "
str_prefix_info         = f"[{color_cyan}INFO{color_end}]\t "
str_prefix_info_red     = f"[{color_red}INFO{color_end}]\t "
error_neither_y_n = f"{str_prefix_err} Please type 'yes' or 'no'"

def is_in_list(item, list):
    # This function searches for a substring within every entry of an array
    # Useful for finding if a URL is in a text file at all, when every line 
    # of the file is a string in the array
    for list_item in list:
        if item in list_item:
            return True
    return False

def erase_blank_lines(list):
    is_str = type(list) is str # How to return variable in the type it was
    if is_str:
        list = list.split("\n")
    for item in list:
        if item.strip() == "":
            del item
    if is_str:
        return "\n".join(list)
    return list


def main():
    book_sale_entries_dict = [] # Used to turn rows into a dictionary to format into RSS or JSON later

    # ==== Get table data from website via Selenium
    url = "https://www.booksalefinder.com/XON.html"
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(200, 1000) # Window size
    driver.get(url)
    all_tables_element = driver.find_elements(By.XPATH, "/html/body/doctype/table/tbody/tr/td/table/tbody/tr/td/p[3]/table")
    for table_num, table_element in enumerate(all_tables_element): # All the tables of the book sale website page that I need
        rows = table_element.find_elements(By.XPATH, "./tbody/tr")
        if len(rows) > 0 and table_num != 0: # If there are rows in this table (and don't run the first table)
            for row_num, row in enumerate(rows): # All the rows in the table
                cells = row.find_elements(By.XPATH, "./td") # All the cells in a row
                if len(cells) == 2: # If there are cells in this row
                    dict_entry_current = {}
                    dict_entry_current['url'] = "https://www.booksalefinder.com/XON.html#"
                    try:
                        # If it is able to find the URL code, put it in the current dict entry
                        dict_entry_current['url'] = dict_entry_current['url']+ row.find_element(By.XPATH, "./td[1]/a").get_attribute('name')
                    except NoSuchElementException:
                        # If no URL found, place an empty string, URL leave as homepage
                        pass
                    cell_text = [cell.text.split("\n") for cell in cells]
                    for cell in cell_text:
                        for line in cells:
                            if line == "":
                                del i
                    dict_entry_current['city'] = cell_text[0][0].strip().split(",")[0]  # First part of first line of first cell
                    dict_entry_current['state'] = cell_text[0][0].strip().split(", ")[1] # Second part of first line of first cell
                    dict_entry_current['address'] = '\n'.join(cell_text[0][1:]).strip() # Entire first cell except first line
                    dict_entry_current['dates'] = cell_text[1][0].strip() # Unformatted line because there are so many variations
                    dict_entry_current['description'] = '\n'.join(cell_text[1][1:]).strip() # Entire second cell except first line
                    # URL specific to that entry row (already inserted above)
                    book_sale_entries_dict.append(dict_entry_current)
    driver.close() 
    options.extensions.clear() # Clear the options that were set
    
    # ==== Process data from tables
    # Some notes that'll help describe the input (variable: 'all_tables'):
    # Table 0: List of book sale dates (ignore this one)
    #   Each cell in row 1 is for a different month, and if a city is in that 
        # cell, that means there's a book sale in that city during that month. 
        # If there's a number in front of it, that's the date. If there's a 
        # "?", date is unknown or ongoing
    # First line in Cell 0 is always "<City>, <Prov/State (2 chars)>"
    # Remaining lines in Cell 0 is address info
    
    # Write dict to JSON
    if bool_output_to_json:
        now = datetime.datetime.now().strftime("%Y %m %d %H%M%S")
        json_filename = f"{output_directory}/{now} results.json"
        with open(json_filename, 'w') as fp:
            json.dump(book_sale_entries_dict, fp)  
        print(f"{str_prefix_info} Wrote to {json_filename}")

    # At this point, the JSON file is written. Now we can make the RSS feed 
    # based on the city
    query_book_sales = [] # Matching results will be stored here for the RSS feed
    for city in query_cities:
        for entry in book_sale_entries_dict:
            if city in entry['city']:
                query_book_sales.append(entry)
    print(f"{str_prefix_info} {len(query_book_sales)} results for {query_cities}")
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
            # TODO: The next 2 lines are temporary to adhere to RSS 2.0 standards
            lines[num] = lines[num].replace("[LINK TO THIS RSS]", "https://husseinesmail.xyz/rss.xml") 
            lines[num] = lines[num].replace("[LINK ALTERNATE]", "https://husseinesmail.xyz") 
        open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'w').writelines(lines)
    
    lines = open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'r').readlines()
    lines_new = [] # Lines to be added to RSS feed
    for posting in query_book_sales:
        # Format description for RSS {START}
        description_tmp = erase_blank_lines(posting['dates']).replace(";", ",") + ". "
        description_tmp = description_tmp.strip()
        description_tmp += erase_blank_lines(posting['address']).replace("\n", ", ") 
        description_tmp = description_tmp.strip()
        description_tmp += erase_blank_lines(posting['description']).replace("\n", ". ")
        posting['description'] = description_tmp.strip()
        # Format description for RSS {END}
        if not is_in_list(posting['url'], lines) and not is_in_list(posting['description'], lines):
            # Duplicate post prevention. Only if matching URL and Description are already in the file.
            # It's possible that this site reuses URLs, which is why I also want to check for matching descriptions.
            # Toronto Reference Library may always use https://www.booksalefinder.com/XON.html#X5222
            # But the dates in the description would be different
            post_date = format_datetime(datetime.datetime.now(datetime.timezone.utc), usegmt=True)
            lines_new.append(f"<item>")
            address_first_line = posting['address'].split('\n')[0]
            lines_new.append(f"<title>Book Sale at {address_first_line}, {posting['city']}</title>")
            lines_new.append(f"<pubDate>{post_date}</pubDate>") # Ex. 2021-07-28T20:57:31Z
            lines_new.append(f"<link>{posting['url']}</link>") # Original RSS uses entry.links[0]['href']. .id is neater, and title doesn't need to be in link
            # Adding author of post
            lines_new.append(f"<author>Booksalefinder</author>")
            # <category term="VSCO" label="VSCO - @veronicaapereiraa"/>
            lines_new.append(f"<category>Book sale at {address_first_line}</category>")
            lines_new.append(f"<guid>{posting['url']}</guid>") # GUID: Unique identifier
            posting['dates'] = posting['dates'].replace(";", ",")
            lines_new.append("<description>" + posting['description'] + "</description>")
            lines_new.append(f"</item>") # End of RSS post
        else:
            print(f"{str_prefix_warn} Did not add {posting['url']} - already present")
            # if not is_in_list(posting['url'], lines) and is_in_list(posting['description'], lines):
    # Write new lines to RSS file
    lines_new = [line + "\n" for line in lines_new] # Done for formatting
    # print(''.join(lines_new))
    rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT) # Find the RSS Delimiter out of the stripped version of the array (each line stripped)
    lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array at the RSS delimiter position
    open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'w').writelines(lines) # Replace previous RSS lines
    print(f"{str_prefix_info} Wrote to {RSS_FILE_NAME}")

    sys.exit()


if __name__ == "__main__":
    main()
