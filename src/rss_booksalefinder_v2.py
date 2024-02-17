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

    v2: TODO

'''

import os
import sys
import requests # Get HTML request from library websites
import itertools # Used to remove duplicates of a list of lists

from bs4 import BeautifulSoup

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
    
    # First get all the table elements on the page (all entries are as columns in these but not all in the same table, must be merged first)
    # /html/body/doctype/table/tbody/tr/td/table/tbody/tr/td/p[3]/table[8]
    # /html/body/doctype/table/tbody/tr/td/table/tbody/tr/td/p[3]/table[8]
    # arr_tables = root.xpath("//doctype/table/tbody/tr/td/table/tbody/tr/td/p[3]/table")
    # //html/body/table/tr/td/table/tr/td/table
    
    response = requests.get(url)
    html = response.content
    # print(response) # "<Response [200]>" = Successful connection (not a string)
    # all_printed_lines.append(response)
    soup = BeautifulSoup(html, features='html.parser')

    # /html/body/doctype/table/tbody/tr/td/table/tbody/tr/td/p[3]
    # console.log(document.getElementsByTagName("TABLE")[0].innerText)
    # console.log(document.getElementsByXPath("/html/body/doctype/table/tbody/tr/td/table/tbody/tr/td/p")[3].innerText)
    # console.log( getElementsByXpath("/html/body/doctype/table/tbody/tr/td/table/tbody/tr/td/p")[3].innerText)

    # book_tables = soup.findAll('table', attrs={'baseURI': 'https://www.booksalefinder.com/XON.html#X5102'})
    book_tables = soup.findAll('table')
    print(f"{len(book_tables)} tables found") 
    all_printed_lines.append(f"{len(book_tables)} tables found")
    all_data = []
    for table in book_tables:
        # print(f"{len(table.find_all('tr'))} 'tr's found")
        # all_printed_lines.append(f"{len(table.find_all('tr'))} 'tr's found")
        # Initialize a list to store your data
        data = []

        # Iterate over each row in the table (skip the header row if necessary)
        for row in table.find_all('tr'):
            # Extract the text from each cell in the row
            # and add it to a list representing that row
            cols = row.find_all('td')
            cols = [element.text.strip() for element in cols]
            # Ensure that you have data (ignore empty/invalid rows)
            if cols:
                data.append(cols)

        # Now 'data' is a list of lists, with each sublist representing a row in the table
        # print(data)
        all_data.append(data)
    
    TOcount = 0 # Tracks number of matches (not filtering for duplicates)
    results = []
    # Look at each entry for "Toronto" and add the matching results to a new list that will be printed
    for data in all_data:
        for item1 in data:
            for item2 in item1:
                if "Toronto" in item2:
                    # print("Contains Toronto")
                    # all_printed_lines.append("Contains Toronto")
                    results.append(item1)
                    TOcount += 1
    print(f"Number of times the string 'Toronto' is found: {TOcount}")
    all_printed_lines.append(f"Number of times the string 'Toronto' is found: {TOcount}")
    
    results.sort() # Sort the array of Toronto results
    results2 = list(results for results,_ in itertools.groupby(results)) # Remove duplicates?
    # print(results2)
    for table_num, item in enumerate(results2): # For all tables
        print(f"--- Table {table_num}:")
        all_printed_lines.append(f"--- Table {table_num}:")
        for row_num, entry in enumerate(item): # For each row in one table
            tmp = entry.replace('\n', ' ')
            print(f"[{row_num}] {tmp}")
            all_printed_lines.append(f"{row_num}: {tmp}")
        print("\n")
        all_printed_lines.append("\n")
        
    print(f"{TOcount} -> {len(results2)}") # Original number with duplicates to number of unique entries
    all_printed_lines.append(f"{TOcount} -> {len(results2)}")
    if bool_output_to_file:
        from datetime import datetime
        now = datetime.now().strftime("%Y %m %d %H%M%S")
        filename = f"/Users/hussein/Downloads/{now} Booksalefinder.txt"
        with open(filename,"w") as f:
            for i in all_printed_lines:
                f.write(f"{i}\n")
            print("=== Output written to:")
            print(f"=== {filename}")

    sys.exit()


if __name__ == "__main__":
    main()
