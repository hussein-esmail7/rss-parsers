'''
to_rss.py
Hussein Esmail
Created: 2024 05 20 (Mon)
Updated: 2024 05 21 (Tue)
Description: A library that generates the RSS file given file path, adds to it 
    given the post info, and can check if a post already exists given the GUID
'''

import errno # For error messages
import os
import sys

def create_rss(path, title, subtitle):
    # This function creates the RSS file at the given path
    # This also checks the syntax of the given arguments
    # This also creates the parent folder if they don't already exist
    rss_file_template = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/">',
        '    <category term="[TERM]" label="[RSS FEED TITLE]"/>',
        '	<updated>[TIME UPDATED]</updated> <!-- TIME UPDATED --> <!-- Ex: 2021-05-03T15:05:35+00:00 -->',
        '    <!-- <icon></icon> -->',
        '    <!-- <id></id> -->',
        '    <link rel="self" href="[LINK TO THIS RSS]" type="application/atom+xml" />',
        '    <link rel="alternate" href="[LINK ALTERNATE]" type="text/html" />',
        '    <!-- <logo></logo> -->',
        '    <subtitle>[RSS DESCRIPTION]</subtitle>',
        '    <title>[RSS FEED TITLE]</title>',
        '',
        '    <!-- Template:',
        '    <entry>',
        '        <title>TODO</title>',
        '        <published>[TIME CREATED]</published>',
        '        <updated>[TIME UPDATED]</updated>',
        '        <link href="[LINK TO THIS POST]"/>',
        '        <author>',
        '            <name>[AUTHOR]</name>',
        '        </author>',
        '        <category term="[TERM]" label="[RSS FEED TITLE]"/>',
        '        <content type="html">',
        '            [CONTENT]',
        '        </content>',
        '    </entry>',
        '    -->',
        '    ',
        '   <!-- FEEDS START -->',
        '',
        '</feed>'
    ]
    path = os.path.expanduser(path)
    folder = "/".join(path.split("/")[:-1])
    filename = path.split("/")[-1]
    if not filename.endswith(".xml"):
        raise ValueError("[\033[91mERROR\033[0m] Path does not end with '.xml'!")
        sys.exit(1)
    if not os.path.exists(folder): # Make dir if it does not exist
        os.makedirs(folder)
    if not os.path.exists(path):
        lines = rss_file_template
        for num, _ in enumerate(lines):
            lines[num] = lines[num].replace("[RSS FEED TITLE]", title)
            lines[num] = lines[num].replace("[RSS DESCRIPTION]", subtitle)
        open(path, 'w').write("\n".join(lines))
    # else:
    #     print(f"RSS file already exists: {path}")


def __is_in_list(item, list):
    # This function searches for a substring within every entry of an array
    # Useful for finding if a URL is in a text file at all, when every line 
    # of the file is a string in the array
    # Double underscore indicates a private function not visible outside the file
    for list_item in list:
        if item in list_item:
            return True
    return False

def check_post_exists(path: str, url: str, guid: str) -> bool:
    # True: Post exists in RSS file already
    # False: Post does not exist in RSS file
    path = os.path.expanduser(path)
    if not path.endswith(".xml"):
        raise ValueError("[\033[91mERROR\033[0m] Path does not end with '.xml'!")
        sys.exit(1)
    if os.path.exists(path): # If file exists, read only
        lines = open(path, 'r').readlines()
    else: # If no file exists, raise error and exit function
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        sys.exit(1)
    # Check if this post is already in the RSS file
    # Use GUID at first but not every RSS page may use GUIDs
    # If no GUID provided (i.e. provided ""), use the URL as the identifier
    if len(guid) != 0:
        if __is_in_list(f"<guid>{guid}</guid>", lines):
            return True
    else:
        if __is_in_list(f'<link href="{url}"/>', lines):
            return True
    return False


def add_to_rss(path: str, title: str, author: str, date: str, url: str, guid: str, body: str):
    # NOTE: Date string must be in ISO 8601 format
    path = os.path.expanduser(path)
    RSS_POS_INSERT = "<!-- FEEDS START -->" # Line to insert feed posts
    if not path.endswith(".xml"):
        raise ValueError("[\033[91mERROR\033[0m] Path does not end with '.xml'!")
        sys.exit(1)
    if os.path.exists(path): # If file exists, read only
        lines = open(path, 'r').readlines()
    else: # If no file exists, raise error and exit function
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
        sys.exit(1)
    rss_delimiter_pos = -1
    try:    
        rss_delimiter_pos = [line.strip() for line in lines].index(RSS_POS_INSERT) # Find the RSS Delimiter out of the stripped version of the array (each line stripped)
    except Exception as e:
        raise IndexError(f"RSS_POS_INSERT ({RSS_POS_INSERT}) not found in {path}!")
        sys.exit(1) # This line exits the program later on so it doesn't overwrite the file
    # If the post is not in the file, continue adding the current post
    if not check_post_exists(path=path, url=url, guid=guid):
        rss_entry_template = [
            '    <entry>',
            '        <title>[POST TITLE]</title>',
            '        <published>[POST DATE]</published>',
            '        <updated>[POST DATE]</updated>',
            '        <link href="[POST URL]"/>',
            '        <guid>[POST GUID]</guid>',
            '        <author>',
            '            <name>[POST AUTHOR]</name>',
            '        </author>',
            '        <description><![CDATA[',
            '            [POST BODY]',
            '        ]]></description>',
            '    </entry>'
        ]
        description = body
        rss_entry_template = rss_entry_template

        # Replace strings that need to be replaced:
        # description = description.replace("&", "&amp;") # Must be before intentional additions of "&" symbols
        # description = "&lt;p&gt;" + description # Start the first "<p>" element
        # description = description.replace("&#13;", "")
        # description = description.replace("'", "&apos;")
        # description = description.replace('"', "&quot;")
        # description = description.replace("<", "&lt;")
        # description = description.replace(">", "&gt;")
        # description = description.replace("\n", "&lt;/p&gt; &lt;p&gt;") # "</p> <p>"
        # description = description + "&lt;/p&gt;" # End the last "</p>" element
        
        for num, _ in enumerate(rss_entry_template):
            rss_entry_template[num] = rss_entry_template[num].replace("[POST TITLE]", title)
            rss_entry_template[num] = rss_entry_template[num].replace("[POST URL]", url)
            rss_entry_template[num] = rss_entry_template[num].replace("[POST AUTHOR]", author)
            rss_entry_template[num] = rss_entry_template[num].replace("[POST GUID]", guid)
            rss_entry_template[num] = rss_entry_template[num].replace("[POST DATE]", date)
            rss_entry_template[num] = rss_entry_template[num].replace("[POST BODY]", description)
        open(path, 'w').write("\n".join(rss_entry_template))
        lines_new = [line + "\n" for line in rss_entry_template] # Done for formatting
        lines = lines[:rss_delimiter_pos+1] + lines_new + lines[rss_delimiter_pos+1:] # Join the array at the RSS delimiter position
        open(path, 'w').writelines(lines) # Replace previous RSS lines
    else:
        print("Did not add RSS entry")
