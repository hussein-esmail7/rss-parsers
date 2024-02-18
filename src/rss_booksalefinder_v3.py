'''
rss_booksalefinder.py
Hussein Esmail
Created: 2023 12 09
Updated: 2024 02 17
Description: A program that converts book sale postings to RSS feeds by city 
    (mainly focused on Toronto). Refer to N11-P183.

    v1: Uses BeautifulSoup to query all tables. Does not help much because 
    the content I want is in the 8th table and is all in one string in that. 
    Next step: Use lxml via this StackOverflow answer: 
    https://stackoverflow.com/a/28306838/8100123

    v2: The answer above only includes top-level tables (which are only 
    advertisements). Now trying to download the HTML page with wget then 
    passing that to lxml.html

    v3: Going full selenium to get the tables since it has to be loaded 
    via JavaScript first. v3 is copied from v1

'''

import os
import sys
import requests # Get HTML request from library websites
import itertools # Used to remove duplicates of a list of lists

from bs4 import BeautifulSoup

from selenium import webdriver
import os
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
bool_run_in_background  = True
# ========= VARIABLES ===========
bool_output_to_file = True

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
error_neither_y_n = f"{str_prefix_err} Please type 'yes' or 'no'"

def main():
    all_printed_lines = [] # Used to save all printed output to text file
    url = "https://www.booksalefinder.com/XON.html"
    
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.set_window_size(200, 1000) # Window size
    driver.get(url)
    all_tables_element = driver.find_elements(By.XPATH, "/html/body/doctype/table/tbody/tr/td/table/tbody/tr/td/p[3]/table")
    for table_num, table_element in enumerate(all_tables_element): # All the tables of the book sale website page that I need
        # print(f"[Table {table_num}]")
        all_printed_lines.append(f"[Table {table_num}]")
        rows = table_element.find_elements(By.XPATH, "./tbody/tr")
        for row_num, row in enumerate(rows): # All the rows in the table
            # print(f"\t[Row {row_num}]")
            all_printed_lines.append(f"\t[Row {row_num}]")
            cells = row.find_elements(By.XPATH, "./td") # All the cells in a row
            for cell_num, cell in enumerate(cells):
                cell_text_tmp = cell.text.split("\n")
                cell_lines_count = len(cell_text_tmp)
                # print(f"\t\t[Cell {cell_num}]: {cell_text_tmp}")
                all_printed_lines.append(f"\t\t[Cell {cell_num}]: (in {cell_lines_count} lines)")
                for line in cell_text_tmp:
                    all_printed_lines.append(f"\t\t\t{line}")

    if bool_output_to_file and len(all_printed_lines) > 0:
        from datetime import datetime
        now = datetime.now().strftime("%Y %m %d %H%M%S")
        filename = f"/Users/hussein/Downloads/{now} Booksalefinder.txt"
        with open(filename,"w") as f:
            for i in all_printed_lines:
                f.write(f"{i}\n")
            print(f"{str_prefix_info} Output written to {filename}")

    driver.close()    
    sys.exit()


if __name__ == "__main__":
    main()
