'''
rss_reddit_imgdl.py
Hussein Esmail
Created: 2021 11 11
Updated: 2022 01 01
Description: This program looks at Reddit RSS feed files, and downloads an
    offline copy of all images an videos (whatever it can) so that the images
    can be viewed offline. This is meant to reduce the number of times the user
    needs to open a browser while looking at their RSS feed reader.
'''

import os               # Used for checking file paths
import sys              # Used for exiting program and temporary print lines
import re               # Used to find image URLs in file
import urllib.request   # Used for getting the initial RSS file
import validators       # Used to check URLs
import time             # Used for delaying download requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By

# ========= VARIABLES ===========
RSS_FOLDER              = os.path.expanduser("~/Documents/Local-RSS/Offline/")
RSS_URLS                = RSS_FOLDER + "urls"
path_img_save           = RSS_FOLDER + "Media/"

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

# ========= LOADING STRINGS =========
don0 = f"[{color_cyan} / {color_end}]\t "
don1 = f"[{color_cyan} - {color_end}]\t "
don2 = f"[{color_cyan} \ {color_end}]\t "
don3 = f"[{color_cyan} | {color_end}]\t "

msg_error_not_reddit    = str_prefix_err + "Not a subreddit RSS URL"
msg_error_not_url       = str_prefix_err + "Not a URL: "
q_print_contents        = str_prefix_q + "Print file contents? "
done_rss_written        = str_prefix_done + "RSS File written"
str_reddit_image_url    = "https://i.redd.it"
urls_to_convert         = []

def yes_or_no(str_ask):
    while True:
        y_n = input(f"{str_prefix_q} {str_prefix_y_n} {str_ask}").lower()
        if y_n[0] == "y":
            return True
        elif y_n[0] == "n":
            return False
        if y_n[0] == "q":
            sys.exit()
        else:
            print(f"{str_prefix_err} {error_neither_y_n}")

def main():
    """
    1. Get Reddit feed from URL
    2. Look for base URLs (ex: "https://i.redd.it/")
    3. Download image
    4. Replace entire found URL in new file
    5. Save entire new file as .xml in a file path

    Notes:
    - Step 4 is not with step 2 because the program may not be able to get the
    media.
    """

    if not os.path.exists(RSS_FOLDER):
        os.mkdir(RSS_FOLDER)
    if not os.path.exists(path_img_save):
        os.mkdir(path_img_save)
    if not os.path.exists(RSS_URLS):
        open(RSS_URLS, 'w').write("# URLs for rss_reddit_imgdl.py go here\n")
        print(f"{str_prefix_err}: No URLs in {RSS_URLS}. Please add URLs to the file and rerun this program.")
        sys.exit(1)

    # Read and parse urls file
    url_file_lines = open(RSS_URLS, 'r').readlines()
    for line in url_file_lines:
        # This is for processing URLs and removing comments and whitespace
        line_first_word = line.split()[0] # Get first word (since URLs don't have spaces)
        if line_first_word[0] != "#":
            # If it is not a comment
            # Treat it as a link. The link checker will verify if it is valid
            urls_to_convert.append(line_first_word)
    for URL_get in urls_to_convert:
        # Check if it is a URL or file location
        if validators.url(URL_get) or URL_get.startswith("file://"):
            file_path_used = ""
            type_used = "NULL" # Online URL or local file
            # Download the RSS file contents
            if validators.url(URL_get):
                options = Options() # Used for running in background
                options.add_argument("--headless")  # Runs in background
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.get(URL_get) # Open the profile page
                file_decoded = driver.find_element(By.XPATH, "/html/body/pre").text
                driver.close()
                type_used = "URL"
            elif os.path.exists(URL_get.replace("file://", "")):
                file_path_used = URL_get.replace("file://", "")
                file_decoded = ''.join(open(file_path_used, 'r').readlines()).replace("\n", "")
                type_used = "FILE"
            # Calculate RSS file name
            if type_used == "URL": # If the link is a Reddit URL
                rss_file_name = URL_get[URL_get.index("/r/")+3:]
            elif type_used == "FILE": # If the link is a file URL
                rss_file_name = file_path_used
            rss_file_name = rss_file_name[:re.search(r'\W+', rss_file_name).start()] + ".xml"
            # Look for base URLs (ex: "https://i.redd.it/")
            regex_link = re.compile("(https|http):\/\/i.redd.it\/(\w+){13}.(jpg|jpeg|png)")
            file_decoded_tmp1 = ";".join(file_decoded.split("&")).split(";")
            links_in_file = []
            for line in file_decoded_tmp1:
                if re.match("(https|http):\/\/i.redd.it\/(\w+){13}.(jpg|jpeg|png)", line):
                    links_in_file.append(line)
            if len(links_in_file) == 1:
                print("1 item to download")
            else:
                print(str(len(links_in_file)) + " items to download")
            for link in links_in_file: # For all found URLs
                if "i.redd.it" in link or "i.imgur.com" in link:
                    # Simple urllib.request save
                    img_name = link.split("/")[-1] # Get image name from URL
                    if link.startswith("https://"):
                        # Loading print statements
                        # There has to be a few seconds in between requests
                        sys.stdout.write("\r" + don0)
                        time.sleep(0.75)
                        sys.stdout.flush()
                        sys.stdout.write("\r" + don1)
                        time.sleep(0.75)
                        sys.stdout.flush()
                        sys.stdout.write("\r" + don2)
                        time.sleep(0.75)
                        sys.stdout.flush()
                        sys.stdout.write("\r" + don3)
                        time.sleep(0.75)

                        # Save image
                        urllib.request.urlretrieve(link, path_img_save + img_name) # Save image
                        # Replace entire found URL in new file (all instances)
                        file_decoded = re.sub(link, "file://" + path_img_save + img_name, file_decoded)
                        sys.stdout.write("\r")
                        print(str_prefix_done + "Saved " + link)
                    # TODO: Imgur links
                # TODO: Reddit Gallery links
            # Save entire new file as .xml in a file path
            with open(RSS_FOLDER + rss_file_name, "w") as f:
                f.write(file_decoded)
            print(done_rss_written)
        else: # Inputted string is not URL
            print(msg_error_not_url + URL_get)
    sys.exit()

if __name__ == "__main__":
    main()
