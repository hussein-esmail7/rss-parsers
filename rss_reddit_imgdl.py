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

    # VARIABLES
    msg_error_not_reddit = "[ERROR] Not a subreddit RSS URL"
    # Get Reddit feed from URL
    # TODO: This part will use sys.argv later
    URL_get = "https://reddit.com/r/unixporn/search.rss?q=flair:'Screenshot'&sort=new&restrict_sr=on&feature=legacy_search"
    # Checks if it is a Reddit RSS first
    if len(re.findall(r"(?<=/r/)(.*)(?=/)*.rss", URL_get)) > 0:
        title_subreddit = re.findall(r"(?<=/r/)(.*)(?=/)", URL_get)[0]
    else:
        print(msg_error_not_reddit)
        sys.exit(1)
    # print(title_subreddit) # "unixporn"
    # Download the file contents
    file = urllib.request.urlopen(URL_get)
    # Decode all file lines
    file_decoded = [line.decode("utf-8") for line in urllib.request.urlopen(URL_get)]
    # print(len(file_decoded))

    
    # Parse XML from temp file
    et = xml.etree.ElementTree.parse(file_decoded)
    # et = xml.etree.ElementTree.parse('file.xml')
    # Append new tag: <a x='1' y='abc'>body text</a>
    new_tag = xml.etree.ElementTree.SubElement(et.getroot(), 'a')
    new_tag.text = 'body text'
    new_tag.attrib['x'] = '1' # must be str; cannot be an int
    new_tag.attrib['y'] = 'abc'
    # Write back to file
    #et.write('file.xml')
    et.write('file_new.xml')



    # Look for base URLs (ex: "https://i.redd.it/")
    



    # Download image




    # Replace entire found URL in new file




    # Save entire new file as .xml in a file path






    sys.exit()


if __name__ == "__main__":
    main()
