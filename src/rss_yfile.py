'''
rss_yfile.py
Hussein Esmail
Created: 2021 08 03
Updated: 2021 09 22
Description: This program converts YFile articles to RSS.
'''

import os                       # Used to navigate directories
import sys                      # Used to exit program
from lxml import html as ht     # Used to parse HTML
from lxml import etree
import feedparser               # Used to get RSS feed to get post links
import requests                 # Used to get HTML
import urllib                   # Used to copy template RSS file from my Github

# == User-configurable variables
RSS_FOLDER = os.path.expanduser("~/.config/rss-parsers/")
RSS_FILENAME = "yfile.xml"
RSS_TITLE = "YFile"
RSS_TERM = "YFile"  # TODO: YFile uses many terms in each post as categories. Add functionality for this later
RSS_DESCRIPTION = "York University' Journal of Record"
BOOL_QUIET = True               # Quiet mode

# == Other global variables
RSS_LINES_REMOVE = ['<!-- <icon></icon> -->', '<!-- <id></id> -->', '<!-- <logo></logo> -->', '<link rel="self" href="[LINK TO THIS RSS]" type="application/atom+xml" />', '<link rel="alternate" href="[LINK ALTERNATE]" type="text/html" />']
RSS_POS_INSERT = "<!-- FEEDS START -->"                                 # Used for RSS feed posts - Where to insert after
URL_RSS = "https://yfile.news.yorku.ca/feed/atom/"                      # YFile RSS URL
URL_TEMPLATE_RSS = "https://raw.githubusercontent.com/hussein-esmail7/templates/master/templaterss.xml" # Template RSS on my Github that this program relies on

def main():
    newsFeed = feedparser.parse(URL_RSS)                                # Get RSS feed from the internet
    lines_new = []
    for entry in newsFeed.entries:                                      # For every post
        content_id = entry.id.split("=")[-1]                            # Link ID
        content_desc = ""                                               # RSS Description per post
        continue_getting_post = True
        if os.path.exists(RSS_FOLDER + RSS_FILENAME):                   # Make RSS if it does not exist
            lines_joined = ''.join(open(RSS_FOLDER + RSS_FILENAME, 'r').readlines())
            continue_getting_post = entry.id not in lines_joined        # If post is already in file or not
        if continue_getting_post:                                       # If post is not already in file
            site_html = ht.fromstring(requests.get(entry.id).content)   # Get HTML
            content_element = site_html.xpath(f'//*[@id="post-{content_id}"]/*[@class="entry-content"]')
            if len(content_element) > 0:                                # If given valid data
                content_desc = etree.tostring(content_element[0]).decode('utf-8')
                content_desc = content_desc.replace("\n", "")
                content_desc = content_desc.replace("\t", "")
                content_desc = content_desc.replace("&#13;", "")        # :before and :after (not needed)
                content_desc = content_desc.replace("&", "&amp;")       # Replace HTML elements in RSS description
                content_desc = content_desc.replace("'", "&apos;")  
                content_desc = content_desc.replace('"', "&quot;")
                content_desc = content_desc.replace("<", "&lt;")
                content_desc = content_desc.replace(">", "&gt;")
                lines_new.append(f"\t<entry>")
                lines_new.append(f"\t\t<title>{entry.title}</title>")
                lines_new.append(f"\t\t<published>{entry.published}</published>") # Ex. 2021-07-28T20:57:31Z
                lines_new.append(f"\t\t<updated>{entry.published}</updated>")
                lines_new.append(f"\t\t<link href=\"{entry.id}\"/>")    # Original RSS uses entry.links[0]['href']. .id is neater, and title doesn't need to be in link
                lines_new.append(f"\t\t<author>")
                lines_new.append(f"\t\t\t<name>{entry.author}</name>")
                lines_new.append(f"\t\t</author>")
                lines_new.append(f"\t\t<category term=\"{RSS_TERM}\" label=\"{RSS_TITLE}\"/>")
                lines_new.append(f"\t\t<content type=\"html\">")
                lines_new.append(content_desc)                          # Only changed item here
                lines_new.append(f"\t\t</content>")
                lines_new.append(f"\t</entry>")
                if not BOOL_QUIET:
                    print(f"[\033[92mDONE\033[0m] {entry.id}")
        elif not BOOL_QUIET:
            print(f"[\033[92mIN FILE\033[0m] {entry.id}")
    if len(lines_new) > 0:                                              # Make RSS feed
        if not os.path.exists(RSS_FOLDER):                              # Make dir if it does not exist
            os.makedirs(RSS_FOLDER)
        if os.path.exists(RSS_FOLDER + RSS_FILENAME):                   # If RSS fole exists, read it only             
            lines = open(RSS_FOLDER + RSS_FILENAME, 'r').readlines()
        else:                                                           # Make RSS if it does not exist
            urllib.request.urlretrieve(URL_TEMPLATE_RSS, RSS_FOLDER + RSS_FILENAME)
            lines = open(RSS_FOLDER + RSS_FILENAME, 'r').readlines()
            for num, _ in enumerate(lines):                             # Replace info in template
                lines[num] = lines[num].replace("[RSS FEED TITLE]", RSS_TITLE).replace("[TERM]", RSS_TERM).replace("[RSS DESCRIPTION]", RSS_DESCRIPTION)
                for rep in RSS_LINES_REMOVE:
                    lines[num] = lines[num].replace('    ' + rep + '\n', "")
            open(RSS_FOLDER + RSS_FILENAME, 'w').writelines(lines)      # Replace template lines with filled in info
        lines_new = [line + "\n" for line in lines_new]                 # Done for formatting
        rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT)
        lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array
        open(RSS_FOLDER + RSS_FILENAME, 'w').writelines(lines)          # Replace previous RSS lines
    sys.exit()

if __name__ == "__main__":
    main()
