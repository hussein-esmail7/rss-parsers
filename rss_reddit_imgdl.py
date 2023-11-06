'''
rss_reddit_imgdl.py
Hussein Esmail
Created: 2021 11 11
Updated: 2022 01 03
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
import argparse         # Parses given arguments
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import *
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By

# ========= VARIABLES ===========
RSS_FOLDER              = os.path.expanduser("~/.config/rss-parsers/reddit_imgdl/")
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
str_prefix_err          = f"[{color_red}ERROR{color_end}]\t "
str_prefix_done         = f"[{color_green}DONE{color_end}]\t "
str_prefix_info         = f"[{color_cyan}INFO{color_end}]\t "

# ========= LOADING STRINGS =========
chars_loading = ["/", "-", "\\", "|"]

msg_error_not_reddit    = str_prefix_err + "Not a subreddit RSS URL"
msg_error_not_url       = str_prefix_err + "Not a URL: "
done_rss_written        = str_prefix_done + "RSS File written"
str_reddit_image_url    = "https://i.redd.it"
urls_to_convert         = []

def main():
    """
    1. Get Reddit feed from URL
    2. Look for base URLs (ex: "https://i.redd.it/")
    3. Download image if it does not exist in the system
    4. Replace entire found URL in new file
    5. Save entire new file as .xml in a file path

    Notes:
    - Step 4 is not with step 2 because the program may not be able to get the
    media.
    """

    # https://www.onlinetutorialspoint.com/python/how-to-pass-command-line-arguments-in-python.html
    parser = argparse.ArgumentParser()

    # Commands to create
    parser.add_argument("-v", "--verbose", action="store_true",help="Verbose mode", dest="verbose")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (overrides --verbose)", dest="quiet")

    args = parser.parse_args()

    if args.verbose and args.quiet:
        print(str_prefix_err + "Cannot have --verbose and --quiet. Using --quiet")
        args.verbose = False

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
        line_first_word = line.strip().split()[0] # Get first word (since URLs don't have spaces)
        if line_first_word[0] != "#":
            # If it is not a comment
            # Treat it as a link. The link checker will verify if it is valid
            urls_to_convert.append(line_first_word)
    for URL_get in urls_to_convert:
        # Check if it is a URL or file location
        if validators.url(URL_get) or URL_get.startswith("file://"):
            if "reddit.com/r/" in URL_get:
                page_name = URL_get.split("r/")[1].split(".")[0]
            else:
                page_name = "/".join(URL_get.split("/")[2:])
            file_path_used = ""
            type_used = "NULL" # Online URL or local file
            # Download the RSS file contents
            if validators.url(URL_get):
                options = Options() # Used for running in background
                options.add_argument("--headless")  # Runs in background
                service = Service(ChromeDriverManager(log_level=0).install())
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
                if "reddit.com" in URL_get:
                    if "/r/" in URL_get:
                        rss_file_name = URL_get[URL_get.index("/r/")+3:]
                    elif "/u/" in URL_get:
                        rss_file_name = URL_get[URL_get.index("/u/")+3:]
            elif type_used == "FILE": # If the link is a file URL
                rss_file_name = file_path_used
            rss_file_name = rss_file_name[:re.search(r'\W+', rss_file_name).start()] + ".xml"
            # Look for base URLs (ex: "https://i.redd.it/")
            regex_link = re.compile("(https|http):\/\/i.redd.it\/([a-zA-Z0-9_-]){13}.(jpg|jpeg|png)")
            file_decoded_tmp1 = ";".join(file_decoded.split("&")).split(";")
            links_in_file = []

            # Determine what URLs are able to be downloaded
            for line in file_decoded_tmp1:
                if re.match("(https|http):\/\/i.redd.it\/(\w+){13}.(jpg|jpeg|png|gif)", line) or re.match("(https|http):\/\/preview.redd.it\/(\w+){13}.(jpg|jpeg|png|gif)?width=([0-9]){1,5}&crop=smart(&auto=webp&s=|&s=)([a-f0-9]){40}", line) or re.match("(https|http):\/\/i.imgur.com\/(\w+){7}.(jpg|jpeg|png|gifv|gif)", line): # i.redd.it or preview.redd.it or i.imgur.com URLs
                    links_in_file.append(line)

            # Leting user know how many items are going to download
            if not args.quiet:
                line_print = str_prefix_info + str(len(links_in_file)) + " item"
                if len(links_in_file) != 1:
                    line_print += "s"
                line_print += " to download from r/" + page_name
                print(line_print)

            for int_current, link in enumerate(links_in_file): # For all found URLs
                images_to_download = []
                if "reddit.com/gallery/" in link:
                    driver = webdriver.Chrome(service=service, options=options)
                    driver.get(link)            # Open the target URL
                    pic_list = driver.find_element(By.XPATH, "//ul").find_elements(By.XPATH, ".//a")
                    for pic in pic_list:
                        pic_url = pic.get_attribute("href").split('?')[0]
                        if pic_url.endswith('.jpg') or pic_url.endswith('.png'):
                            pic_url = pic_url.replace('preview.', 'i.')
                        else:                           # Unknown exceptions
                            print(str_prefix_err + "Video or non-JPG, not done: " + pic_url)
                        images_to_download.append(pic_url) # Add formatted URL to array
                elif "i.redd.it" in link or "i.imgur.com" in link or "preview.redd.it" in link:
                    # Simple urllib.request save

                    # Calculate file name
                    if "preview.redd.it" in link:
                        img_name = link.split("/")[3].split("?")[0].replace(".", "_small.")
                    else: # For i.redd.it and i.imgur.com
                        img_name = link.split("/")[-1] # Get image name from URL

                    if link.startswith("https://") and not os.path.isfile(path_img_save + img_name):
                        # If it is an online image and is not going to replace a saved version
                        # Loading print statements
                        # There has to be a few seconds in between requests
                        if not args.quiet: # If print statements are allowed
                            for line_num, char in enumerate(chars_loading):
                                line_print = "\r[" + color_cyan + " " + char + " " + color_end + "]\t "
                                if not args.verbose: # If normal print selected
                                    line_print += "Saving " + str(int_current) + " of " + str(len(links_in_file))
                                sys.stdout.write(line_print)
                                time.sleep(0.75)
                                if line_num is not len(chars_loading) - 1:
                                    sys.stdout.flush()
                        else: # If user selected quiet mode
                            time.sleep(3)
                        # Save image
                        urllib.request.urlretrieve(link, path_img_save + img_name) # Save image
                        # Replace entire found URL in new file (all instances)
                        file_decoded = re.sub(link, "file://" + path_img_save + img_name, file_decoded)
                        sys.stdout.write("\r")
                        if args.verbose:
                            print(str_prefix_done + "Saved " + link + " (" + str(int_current + 1) + "/" + str(len(links_in_file)) + ")")
                    elif os.path.isfile(path_img_save + img_name):
                        if args.verbose:
                            print("\t\t> Image exists on system")
                    else:
                        print("\t\t> Unknown Exception: " + link)
                # TODO: Reddit Gallery links
                #       The issue with Gallery links is there are multiple
                #       media URLs that replace a single Reddit Gallery URL

            # Replace URLs of the images that are alrady saved in case they are still in the feed
            for saved_image in os.listdir(path_img_save):
                if len(saved_image.split(".")[0]) == 13: # i.redd.it link
                    file_decoded = re.sub("https://i.redd.it/" + saved_image, "file://" + path_img_save + saved_image, file_decoded)
                elif len(saved_image.split(".")[0]) == 7: # i.imgur.com links
                    file_decoded = re.sub("https://i.imgur.com/" + saved_image, "file://" + path_img_save + saved_image, file_decoded)
                # If any other file types found, do nothing. If "_small" found
                # in image, it is preview.redd.it image, but not required
                # hashcode

            # At this point all images have been downloaded and new RSS file is ready to write

            # Save entire new file as .xml in a file path
            with open(RSS_FOLDER + rss_file_name, "w") as f:
                f.write(file_decoded)

            # Inform user that this feed is done
            if not args.quiet:
                print(done_rss_written + " for " + page_name)
            # Loops back to next URL
        else: # Inputted string is not URL
            print(msg_error_not_url + URL_get)
    sys.exit()

if __name__ == "__main__":
    main()
