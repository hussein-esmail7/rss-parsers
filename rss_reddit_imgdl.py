'''
rss_reddit_imgdl.py
Hussein Esmail
Created: 2021 11 11
Updated: 2021 12 29
Description: This program looks at Reddit RSS feed files, and downloads an
    offline copy of all images an videos (whatever it can) so that the images
    can be viewed offline. This is meant to reduce the number of times the user
    needs to open a browser while looking at their RSS feed reader.
'''

import os               # Used for checking file paths
import sys              # Used for exiting program
import re               # Used to find image URLs in file
import urllib.request   # Used for getting the initial RSS file
import validators       # Used to check URLs
from selenium import webdriver
import platform
from selenium.common.exceptions import *
from selenium.webdriver.chrome.options import Options  # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By
import time

# ========= VARIABLES ===========
RSS_FOLDER = os.path.expanduser("~/Documents/Local-RSS/Offline/")
RSS_URLS = RSS_FOLDER + "urls"
path_img_save = os.path.expanduser("~/Documents/Local-RSS/Offline/Media/")
CHROMEDRIVER_LOCATION_LINUX = os.path.expanduser("~/Documents/Coding/py/reference/Chromedriver/chromedriver")
CHROMEDRIVER_LOCATION_MACOS = "/Users/hussein/Documents/Coding/py/reference/Chromedriver/chromedriver"
CHROMEDRIVER_LOCATION_OTHER = "" # Chromedriver path if you are not using macOS or Linux
bool_use_Brave = False
bool_run_in_background = False

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

msg_error_not_reddit    = str_prefix_err + "Not a subreddit RSS URL"
msg_error_not_url       = str_prefix_err + "Not a URL: "
q_print_contents        = str_prefix_q + "Print file contents? "
done_rss_written        = str_prefix_done + "RSS File written"
str_reddit_image_url    = "https://i.redd.it"
urls_to_convert         = []
# urls_to_convert         = ["https://reddit.com/r/unixporn/search.rss?q=flair:'Screenshot'&sort=new&restrict_sr=on&feature=legacy_search"]

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
    # Determining OS type for Chromedriver location
    os_type = platform.platform().split("-")[0]
    if os_type == "Linux":
        chromedriver_path = CHROMEDRIVER_LOCATION_LINUX
    elif os_type == "macOS":
        chromedriver_path = CHROMEDRIVER_LOCATION_MACOS
    else:
        chromedriver_path = CHROMEDRIVER_LOCATION_OTHER

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
        if validators.url(URL_get) or URL_get.startswith("file://"): # Checks if it is a URL or file location
            file_path_used = ""
            type_used = "NULL" # Online URL or local file
            # Download the RSS file contents
            if validators.url(URL_get):
                options = Options() # Used for Chromedriver
                if bool_run_in_background:
                    options.add_argument("--headless")  # Runs in background
                if bool_use_Brave:
                    options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
                    driver = webdriver.Chrome(options=options)
                else:
                    driver = webdriver.Chrome(chromedriver_path, options=options)
                driver.get(URL_get) # Open the profile page
                file_decoded = driver.find_element(By.XPATH, "/html/body/pre").text
                driver.close()
                # file_decoded = urllib.request.urlopen(URL_get)
                # file_decoded = file_decoded.read()
                # file_decoded = file_decoded.decode("utf-8")
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
            link_positions = [m.start() for m in re.finditer(str_reddit_image_url, file_decoded)]
            print(link_positions)
            for link in link_positions:
                # print(str_prefix_info + str(link)) # Print position integer
                file_decoded_tmp = "https://" + file_decoded[link:].split("https://")[1]
                file_decoded_tmp = file_decoded_tmp.split("&")[0].split("?")[0]
                img_url = file_decoded_tmp
                if "i.redd.it" in img_url:
                    print(color_red + "="*50 + color_end)
                    img_name = img_url.split("/")[-1] # Get image name from URL
                    if img_url.startswith("https://"):
                        print(str_prefix_info + img_url + " " + img_name + " -> " + path_img_save + img_name)
                        # print(str_prefix_info + "Saving " + img_name + "... ", end="")
                        urllib.request.urlretrieve(img_url, path_img_save + img_name) # Save image
                        time.sleep(3)
                        # Replace entire found URL in new file
                        file_decoded = file_decoded.replace(img_url, "file://" + path_img_save + img_name)
                        print(str_prefix_done)
            # Save entire new file as .xml in a file path
            with open(RSS_FOLDER + rss_file_name, "w") as f:
                f.write(file_decoded)
            print(done_rss_written)
        else: # Inputted string is not URL
            print(msg_error_not_url + URL_get)
    sys.exit()

if __name__ == "__main__":
    main()
