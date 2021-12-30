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

# ========= VARIABLES ===========
RSS_FOLDER = os.path.expanduser("~/Documents/Local-RSS/Offline/")
RSS_URLS = RSS_FOLDER + "urls"
path_img_save = os.path.expanduser("~/Documents/Local-RSS/Offline/Media/")

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
urls_to_convert         = ["https://reddit.com/r/unixporn/search.rss?q=flair:'Screenshot'&sort=new&restrict_sr=on&feature=legacy_search"]


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
    type_used = "NULL"
    file_path_used = ""
    for URL_get in urls_to_convert:
        if validators.url(URL_get) or URL_get.startswith("file://"): # Checks if it is a URL or file location
            # Download the RSS file contents
            if validators.url(URL_get):
                file_decoded = urllib.request.urlopen(URL_get).read().decode("utf-8")
                type_used = "URL"
            elif os.path.exists(URL_get.replace("file://", ""):
                file_path_used = URL_get.replace("file://", "")
                file_decoded = ''.join(open(file_path_used, 'r').readlines()).replace("\n", "")
                type_used = "FILE"
            # Calculate RSS file name
            if type_used == "URL": # If the link is a Reddit URL
                rss_file_name = URL_get[URL_get.index("/r/")+3:]
            elif type_used == "FILE": # If the link is a file URL
                rss_file_name = file_path_used
            rss_file_name = re.search(r'\W+', rss_file_name).start() + ".xml"
            # Look for base URLs (ex: "https://i.redd.it/")
            link_positions = [m.start() for m in re.finditer(str_reddit_image_url, file_decoded)]
            for link in link_positions:
                img_url = re.match("(.*?)&", file_decoded[link:]).group()[:-1] # Get URL
                img_name = img_url.split("/")[-1] # Get image name from URL
                print("Saving " + img_name + "... ", end="")
                urllib.request.urlretrieve(img_url, path_img_save + img_name) # Save image
                # Replace entire found URL in new file
                file_decoded = file_decoded.replace(img_url, "file://" + path_img_save + img_name)
                print("Done")
            # Save entire new file as .xml in a file path
            with open(RSS_FOLDER + rss_file_name, "w") as f:
                f.write(file_decoded)
            print(done_rss_written)
        else: # Inputted string is not URL
            print(msg_error_not_url + URL_get)
    sys.exit()

if __name__ == "__main__":
    main()
