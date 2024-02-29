'''
rss_citt.py
Hussein Esmail
Created: 2024 02 29
Updated: 2024 02 29
Description: A program that converts CITT theatre job postings to RSS feeds by 
    province (mainly focused on Ontario). Refer to N12-P003.
'''

import sys # To exit the program

import requests # Get HTML request from library websites
from bs4 import BeautifulSoup
import re # Used for allCapsToTitleCase()

import datetime
import urllib.request # To download template RSS document
from email.utils import format_datetime # Convert datetime object to RFC822, which RSS 2.0 requires
import os

# TODO: Posts of the same province are currently written non-consecutively. To fix later
# TODO: Full description formatting in RSS file

# ========= VARIABLES ===========
bool_print_data = False # Print formatted dictionary of job postings of all provinces
output_directory = os.path.expanduser("~/.config/rss-parsers/CITT") # Where to put output files
RSS_FOLDER   = os.path.expanduser("~/.config/rss-parsers/CITT/")
RSS_TERM                = "CITT"
RSS_POS_INSERT          = "<!-- FEEDS START -->" # Line to insert feed posts
URL_TEMPLATE_RSS        = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss2.xml" # Template RSS on my Github that this program relies on

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

def allCapsToTitleCase(string):
    # This function converts words that are in all caps to normal title casing
    # Needed because some city titles may be in all caps.
    # Ex: "CALGARY" -> "Calgary"
    return re.sub('[A-Z]+', lambda x: x.group(0).title(), string)

def is_in_list(item, list):
    # This function searches for a substring within every entry of an array
    # Useful for finding if a URL is in a text file at all, when every line 
    # of the file is a string in the array
    for list_item in list:
        if item in list_item:
            return True
    return False

def main():
    url = "https://www.citt.org/cgi/page.cgi/_jobpostings.html?cmd=zine&parent_id=40"
    # print(url)
    results_formated = []

    response = requests.get(url)
    html = response.content
    # print(response) # "<Response [200]>" = Successful connection (not a string)
    # all_printed_lines.append(response)
    data = []
    soup = BeautifulSoup(html, features='html.parser')
    all_tables = soup.findAll('table')
    if len(all_tables) == 0:
        # Error handling
        # print(f"{str_prefix_err} No tables found!")
        sys.exit()
    table_tbody = all_tables[0].find('tbody')
    rows = table_tbody.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols if ele]) # Get rid of empty values
        entry_unformatted = [ele for ele in cols if ele]
        if len(entry_unformatted) == 6:
            # Columns:
            # 0: Title (also includes URL)
            # 1: Company
            # 2: Job Type
            # 3: Category
            # 4: Location (<City, Province>)
            # 5: Deadline (<Month, DD, YYYY>)
            results_formated.append({
                'title': entry_unformatted[0],
                'company': entry_unformatted[1],
                'jobtype': entry_unformatted[2],
                'category': entry_unformatted[3],
                'location': allCapsToTitleCase(entry_unformatted[4]),
                'deadline': entry_unformatted[5],
                'url': row.find_all('td')[0].find('a', href=True)['href'],
                'description': 'TODO: Description not done' # TODO: Get from each post URL
            })
    # print(data) # Prints all unformatted results
    # TODO: Get description from each post URL
    for entry in results_formated:
        # print("="*30)
        # print(entry['url'])
        response = requests.get(entry['url'])
        html = response.content
        # print(response) # "<Response [200]>" = Successful connection (not a string)
        # all_printed_lines.append(response)
        soup = BeautifulSoup(html, features='html.parser')
        desc_short = soup.find_all("div", {"class": "ZineSummary"})
        desc_full = soup.find_all("div", {"class": "ZineBody"})
        desc_short_text = [r.text.replace('\n\n', "\n").strip() for r in desc_short if r.text.strip()]
        desc_full_text = [r.text.replace('\n\n', "\n").strip() for r in desc_full if r.text.strip()]
        entry['description'] = "\n".join(desc_short_text) + "\n\n" + "\n".join(desc_full_text)
            
    if len(results_formated) == 0: # If no entries found
        print(f"{str_prefix_err} No entries found")
        sys.exit()
    if bool_print_data:
        for entry_num, entry in enumerate(results_formated):
            print(f"Entry {entry_num}/{len(results_formated)} " + "="*20)
            print(" "*4 + f"Title: {entry['title']}")
            print(" "*4 + f"Company: {entry['company']}")
            print(" "*4 + f"Job Type: {entry['jobtype']}")
            print(" "*4 + f"Category: {entry['category']}")
            print(" "*4 + f"Location: {entry['location']}")
            print(" "*4 + f"Deadline: {entry['deadline']}")
            print(" "*4 + f"URL: {entry['url']}")
    # ==============================
    # Onwards: Convert data to RSS
    # ==============================
    for province in ["Alberta", 
                     "British Columbia", 
                     "Manitoba", 
                     "New Brunswick", 
                     "Newfoundland and Labrador", 
                     "Nova Scotia", 
                     "Ontario", 
                     "Prince Edward Island", 
                     "Quebec", 
                     "Saskatchewan",
                     "Northwest Territories", 
                     "Nunavut",
                     "Yukon"]:
        # Make an RSS file per province. The next part gets entries only for 
        # that province. This is useful because otherwise the program might 
        # create an RSS file for a province/territory but there will be no 
        # posts for it (i.e. There's no point in creating "yukon.xml" if there 
        # aren't any posts for it.)
        query = []
        for entry in results_formated:
            if province in entry['location']:
                query.append(entry)
            if province == "Quebec":
                # Account for both "Quebec" and "Québec"
                if "Québec" in entry['location']:
                    query.append(entry)
        if len(query) > 0:
            # If there are posts for this province:
            RSS_TITLE               = f"CITT for {province}"
            RSS_DESCRIPTION         = f"CITT for {province}"
            RSS_FILE_NAME           = f"CITT_{province.replace(' ', '_').lower()}.xml"
            # Check all folders exist and RSS file exists. If not, create them
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
            # End of folder and file (exists) checks
            lines = open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'r').readlines()
            lines_new = [] # Lines to be added to RSS feed
            int_new_posts = len(query)
            for entry in query:
                # Format description for RSS {START}
                entry['description'] = entry['description'].replace("\n", "<br>").strip()
                # Format description for RSS {END}
                if not is_in_list(entry['url'], lines):
                    # Duplicate post prevention. Only if matching URL  are already in the file.
                    post_date = format_datetime(datetime.datetime.now(datetime.timezone.utc), usegmt=True)
                    lines_new.append(f"<item>")
                    location_tmp = entry['location'].split(",")[0]
                    title_tmp = f"{entry['title']} at {entry['company']} in {location_tmp}"
                    lines_new.append(f"<title>{title_tmp}</title>")
                    lines_new.append(f"<pubDate>{post_date}</pubDate>") # Ex. 2021-07-28T20:57:31Z
                    lines_new.append(f"<link>{entry['url']}</link>") # Original RSS uses entry.links[0]['href']. .id is neater, and title doesn't need to be in link
                    # Adding author of post
                    lines_new.append(f"<author>{entry['company']}</author>")
                    # <category term="VSCO" label="VSCO - @veronicaapereiraa"/>
                    lines_new.append(f"<category>Job Post</category>")
                    lines_new.append(f"<guid>{entry['url']}</guid>") # GUID: Unique identifier
                    # entry['dates'] = entry['dates'].replace(";", ",")
                    lines_new.append("<description><![CDATA[" + entry['description'] + "]]></description>")
                    lines_new.append(f"</item>") # End of RSS post
                else:
                    int_new_posts =- 1
        if int_new_posts > 0:
            print("\t" + f"{int_new_posts} new posts ({province})")
        if len(lines_new) != 0:
            lines_new = [line + "\n" for line in lines_new] # Done for formatting
            # print(''.join(lines_new))
            rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT) # Find the RSS Delimiter out of the stripped version of the array (each line stripped)
            lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array at the RSS delimiter position
            open(RSS_FOLDER + f"{RSS_FILE_NAME}", 'w').writelines(lines) # Replace previous RSS lines
            print(f"{str_prefix_info} Wrote to {RSS_FILE_NAME}")

    sys.exit() # Exit the program

if __name__ == "__main__":
    main()
