'''
rss_booksalefinder.py
Hussein Esmail
Created: 2022 02 17
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

'''

import os
import sys
import requests # Get HTML request from library websites
import lxml.html as LH
import pandas as pd
import wget

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

def text(elt):
    return elt.text_content().replace(u'\xa0', u' ')

def main():
    all_printed_lines = [] # Used to save all printed output to text file
    url = "https://www.booksalefinder.com/XON.html"
    output_directory = "/Users/hussein/Downloads/"
    # filename = wget.download(url, out=output_directory)
    # os.system("google-chrome --headless --dump-dom --virtual-time-budget=10000 --timeout=10000 --run-all-compositor-stages-before-draw --disable-gpu --user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36' 'https://www.booksalefinder.com/XON.html' > /Users/hussein/Downloads/XON.html")
    
    
    
    r = requests.get(url)
    with open(output_directory + "XON.html", "r") as f:
        page = f.read()
    root = LH.fromstring(page)
    all_tables = []

    # for table in root.xpath('//table[@id="sortabletable"]'):
    for table in root.xpath('//table'):
        header = [text(th) for th in table.xpath('//th')]        # Column names
        data = [[text(td) for td in tr.xpath('td')]  
                for tr in table.xpath('//tr')]                   # 2
        data = [row for row in data if len(row)==len(header)]    # 3 
        data = pd.DataFrame(data, columns=header)                # 4
        all_tables.append(data)
        print(f"TABLE " + "="*20)
        print(data)
        all_printed_lines.append(f"TABLE " + "="*20)
        all_printed_lines.append(data)



    if bool_output_to_file and len(all_printed_lines) > 0:
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
