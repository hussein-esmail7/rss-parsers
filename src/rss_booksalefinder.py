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

import to_rss

# ========= VARIABLES ===========
bool_run_in_background  = True # Hide selenium Chrome window
bool_output_to_json = False 
query_cities = ['Toronto'] # Cities that go into the RSS file
rss_title                = "Booksalefinder"
rss_subtitle = "Booksalefinder.com RSS Feed"
# RSS_TITLE               = f"Booksalefinder for {', '.join(query_cities)}"
# RSS_DESCRIPTION         = f"Booksalefinder for {', '.join(query_cities)}"

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

def is_internet_connected():
    try:
        urllib.request.urlopen('http://google.com')
        return True
    except:
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
    path = "~/.config/rss-parsers/Booksalefinder/" # Separate variable for the JSON option
    rss_path = path + "booksalefinder.xml"
    color_sponsor = "#ffff99" # Colour of the background element if it's sponsorted (URLs are found a different way if this is true)
    book_sale_entries_dict = [] # Used to turn rows into a dictionary to format into RSS or JSON later
    if not is_internet_connected():
        print(f"{str_prefix_err}You're not connected to the internet!")
        sys.exit(1)
    # ==== Get table data from website via Selenium
    url = "https://www.booksalefinder.com/XON.html"
    
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    driver = webdriver.Chrome(service=Service(), options=options)
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
                    try:
                        # If it is able to find the URL code, put it in the current dict entry
                        dict_entry_current['url'] = dict_entry_current['url'] + row.find_element(By.XPATH, "./td[1]/a").get_attribute('name')
                        dict_entry_current['sponsor'] = False
                        book_sale_entries_dict.append(dict_entry_current)
                    except NoSuchElementException:
                        # If no URL found, it's possible it's sponsored
                        try:
                            if row.get_attribute('bgcolor') == color_sponsor:
                                # Sponsored post
                                dict_entry_current['sponsor'] = True
                                dict_entry_current['url'] = row.find_element(By.XPATH, "./td[1]/p[1]/a[1]").get_attribute('name')
                                book_sale_entries_dict.append(dict_entry_current)
                            else: 
                                raise Exception()
                        except:
                            print(f"{str_prefix_err} No specific URL found! (Table {table_num}, row {row_num})")
                            print(f"\t{dict_entry_current['city']}")
                            print(f"\t{dict_entry_current['state']}")
                            print(f"\t{' '.join(dict_entry_current['address'])}")
                            print(f"\t{' '.join(dict_entry_current['dates'])}")
                    # URL specific to that entry row (already inserted above)
                    
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
        json_filename = f"{path}/{now} results.json"
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
    # print(f"{str_prefix_info} {len(query_book_sales)} results for {query_cities}")
    to_rss.create_rss(rss_path, rss_title, rss_subtitle) # Create file if does not exist
    int_new_posts = 0
    for posting in query_book_sales:
        # Format description for RSS {START}
        description_tmp = erase_blank_lines(posting['dates']).replace(";", ",") + ". "
        description_tmp = description_tmp.strip()
        description_tmp += erase_blank_lines(posting['address']).replace("\n", ", ") 
        description_tmp = description_tmp.strip()
        description_tmp += erase_blank_lines(posting['description']).replace("\n", ". ")
        posting['description'] = description_tmp.strip()
        # Format description for RSS {END}
        if not to_rss.check_post_exists(rss_path, posting['url'], posting['url']):
            # Duplicate post prevention. Only if matching URL and Description are already in the file.
            # It's possible that this site reuses URLs, which is why I also want to check for matching descriptions.
            # Toronto Reference Library may always use https://www.booksalefinder.com/XON.html#X5222
            # But the dates in the description would be different
            date_formatted = format_datetime(datetime.datetime.now(datetime.timezone.utc), usegmt=True)
            address_first_line = posting['address'].split('\n')[0]
            title = f"Book Sale at {address_first_line}, {posting['city']}</title>"
            if posting['sponsor'] == True:
                title = "[Sponsor] " + title
            to_rss.add_to_rss(rss_path, title, author="Booksalefinder", date=date_formatted, url=posting['url'], guid=posting['url'], body=posting['description'])
            int_new_posts += 1
    
    if int_new_posts > 0:
        print("\t" + str(int_new_posts) + " new posts")
    sys.exit()


if __name__ == "__main__":
    main()
