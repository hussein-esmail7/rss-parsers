'''
rss_reddit_imgdl.py
Hussein Esmail
Created: 2021 11 11
Updated: 2021 11 11
Description: This program looks at Reddit RSS feed files, and downloads an
    offline copy of all images an videos (whatever it can) so that the images
    can be viewed offline. This is meant to reduce the number of times the user
    needs to open a browser while looking at their RSS feed reader.
'''


import os
import sys
import re # Used to extract subreddit name from URL
import urllib.request # Used for getting the initial RSS file
import xml.etree.ElementTree # Used to parse, edit, and export XML
import re

# ========= VARIABLES ===========
path_rss_save = "/home/hussein/Downloads/"
path_img_save = "/home/hussein/Downloads/reddit/"

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

msg_error_not_reddit = "[ERROR] Not a subreddit RSS URL"

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

    if yes_or_no("Use from file? "):
        bool_continue_asking = True
        file_decoded = ""
        # "/Users/hussein/Downloads/unixporn.txt"
        while bool_continue_asking:
            file_decoded = input("File path to use: ")
            bool_continue_asking = not yes_or_no("Is this correct: " + file_decoded + "? ")
        file_decoded = open(file_decoded, "r").readlines()
    else:
        # Get Reddit feed from URL
        # TODO: This part will use sys.argv later
        URL_get = "https://reddit.com/r/unixporn/search.rss?q=flair:'Screenshot'&sort=new&restrict_sr=on&feature=legacy_search"

        # Checks if it is a URL
        if not validators.url(URL_get):
            print("This is not a URL!")
            sys.exit(1)

        # Download the RSS file contents
        file_decoded = urllib.request.urlopen(URL_get).read().decode("utf-8")
    if yes_or_no("Print file contents? "):
        print(file_decoded)

    # Look for base URLs (ex: "https://i.redd.it/")
    #print("".join(file_decoded).find("https://i.redd.it"))
    link_positions = [m.start() for m in re.finditer("https://i.redd.it", file_decoded)]
    print("There are " + str(len(link_positions)) + " image URLs")
    print("Indexes of image URLs (start positons): ", end="")
    print(link_positions)
    
    file_new = file_decoded # file_new is copy of RSS with edited URLs
    for link in link_positions:
        img_url = re.match("(.*?)&", file_decoded[link:]).group()[:-1] # Get URL
        # Download image
        img_name = img_url.split("/")[-1] # Get image name from URL
        print("Saving " + img_name + "... ", end="")
        urllib.request.urlretrieve(img_url, path_img_save + img_name) # Save image
        # Replace entire found URL in new file
        file_new = file_new.replace(img_url, "file://" + path_img_save + img_name)
        print("Done")
    # Save entire new file as .xml in a file path
    with open(path_rss_save + "rss1.xml", "w") as f:
        f.write(file_new)
    print("RSS File written")
    sys.exit()

if __name__ == "__main__":
    main()
