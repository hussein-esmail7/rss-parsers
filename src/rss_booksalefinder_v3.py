'''
rss_booksalefinder_v3.py
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

from selenium import webdriver
import os
import sys # To exit the program
from selenium import webdriver
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)
from datetime import datetime

# ========= VARIABLES ===========
bool_run_in_background  = True # Hide selenium Chrome window
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

    # ==== Get table data from website via Selenium
    url = "https://www.booksalefinder.com/XON.html"
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    # TODO: Received the following warning when running:
    # DeprecationWarning: executable_path has been deprecated, please pass in a Service object
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.set_window_size(200, 1000) # Window size
    driver.get(url)
    all_tables_element = driver.find_elements(By.XPATH, "/html/body/doctype/table/tbody/tr/td/table/tbody/tr/td/p[3]/table")
    all_tables = []
    for table_num, table_element in enumerate(all_tables_element): # All the tables of the book sale website page that I need
        all_printed_lines.append(f"[Table {table_num}]")
        rows = table_element.find_elements(By.XPATH, "./tbody/tr")
        table_toappend = []
        if len(rows) > 0: # If there are rows in this table
            rows_toappend = []
            for row_num, row in enumerate(rows): # All the rows in the table
                all_printed_lines.append(f"\t[Row {row_num}]")
                cells = row.find_elements(By.XPATH, "./td") # All the cells in a row
                if len(cells) > 0: # If there are cells in this row
                    cells_toappend = []
                    for cell_num, cell in enumerate(cells):
                        cell_text_tmp = cell.text.split("\n")
                        for i in cell_text_tmp:
                            if i == "":
                                del i
                        cells_toappend.append(cell_text_tmp)
                        all_printed_lines.append(f"\t\t[Cell {cell_num}]: (in {len(cell_text_tmp)} lines)")
                        for line in cell_text_tmp:
                            all_printed_lines.append(f"\t\t\t{line}")
                    rows_toappend.append(cells_toappend) # Append the cell to all rows
            table_toappend.append(rows_toappend) # Append all rows to the table
        all_tables.append(table_toappend) # Append the table to all tables
    driver.close() 
    
    # ==== Process data from tables
    # Some notes that'll help describe the input (variable: 'all_tables'):
    # Table 0: List of book sale dates (ignore this one)
    #   Each cell in row 1 is for a different month, and if a city is in that 
        # cell, that means there's a book sale in that city during that month. 
        # If there's a number in front of it, that's the date. If there's a 
        # "?", date is unknown or ongoing
    # First line in Cell 0 is always "<City>, <Prov/State (2 chars)>"
    # Remaining lines in Cell 0 is address info
    
    # Combine all tables except the 0th so all rows are together (since one 
    # row is also an entry for a book sale)
    table_0 = all_tables[0]
    book_sale_entries_unformatted = []
    for table in all_tables[1:]:
        for row in table:
            for i in row:
                book_sale_entries_unformatted.append(i)
    # Format the rows into a dictionary now
    book_sale_entries_dict = []
    print(len(book_sale_entries_unformatted))
    # print(book_sale_entries_unformatted)
    for row in book_sale_entries_unformatted:
        # try:
        #     print(row[1][1][1])
        # except:
        #     pass
        try:
            tmp_dates = row[1][0].strip()
        except IndexError:
            tmp_dates = "N/A"
        try:
            tmp_description = '\n'.join(row[1][1:]).strip()
        except IndexError:
            tmp_description = "N/A"

        book_sale_entries_dict.append({
            'city': row[0][0].strip().split(",")[0],  # First part of first line of first cell
            'state': row[0][0].strip().split(", ")[1], # Second part of first line of first cell
            'address': '\n'.join(row[0][1:]).strip(), # Entire first cell except first line
            'dates': tmp_dates, # Unformatted line because there are so many variations
            'description': tmp_description # Entire second cell except first line
        })
    # At this point we have a dictionary of all book sales
    # Now we can filter by city
    entry_count = 0
    for entry in book_sale_entries_dict:
        if "Toronto" in entry['city']:
            entry_count += 1
            print(f"== ENTRY #{entry_count} ==")
            print("\tAddress:")
            for line in entry['address'].split('\n'):
                print(f"\t\t{line.strip()}")
            print(f"\tDates: {entry['dates']}")
            print(f"\tDescription:")
            for line in entry['description'].split('\n'):
                print(f"\t\t{line.strip()}")
    # Write dict to JSON
    now = datetime.now().strftime("%Y %m %d %H%M%S")
    import json
    filename = f"/Users/hussein/Downloads/{now} results.json"
    with open(filename, 'w') as fp:
        json.dump(book_sale_entries_dict, fp)            

    # ==== Write all output to text file
    if bool_output_to_file and len(all_printed_lines) > 0: 
        # If there are also lines to be printed (i.e. don't make an empty text file)
        
        filename = f"/Users/hussein/Downloads/{now} Booksalefinder.txt"
        with open(filename,"w") as f:
            for i in all_printed_lines:
                f.write(f"{i}\n")
            print(f"{str_prefix_info} Output written to {filename}")

    sys.exit()


if __name__ == "__main__":
    main()
