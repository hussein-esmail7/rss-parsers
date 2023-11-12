'''
rss_html.py by  
Hussein Esmail
Created: 2021 05 05
Updated: 2021 08 03
'''
description = [ "This inputs an HTML file in the arguments and converts a copy of it to\n",
                "an RSS format where in-item URLs are supported in Newsboat (like on \n",
                "Reddit RSS pages, because if I prefer them then someone else probably\n",
                "does too).\n"]

import os           # Used to navigate directories
import sys          # Used to get CLI arguments
import datetime     # Used to make RSS time format
import pyperclip    # Used to copy text to clipboard as an output method
import validators   # Used to check validity of a URL
import csv          # Used to read CSV file data
import operator     # Used to manipulate CSV data

# TODO: Check if .csv file exists before accessing
# TODO: If a relative link is present (ex: /contact), change it to the full link in the RSS post

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

# ========= ERROR MESSAGE VARIABLES =========
error_input_html        = "You need to input an HTML file to convert.\n\t  Type -h or --help for help."
error_too_many_args     = "You typed more arguments than I expected. Please verify and try again."
error_not_an_int        = "I didn't like that input! Please type an int."
error_incorrect_args    = "I don't know what you gave me... but it wasn't an HTML file."
error_no_title          = "You didn't select a title. Please restart the program."
error_no_out_choice     = "You gotta pick something, dude."
error_neither_y_n       = "The first character must either be a 'y' or 'n'."
error_invalid_url       = "This is not a valid URL."

# ========= INFORMATION MESSAGES =========
message_rss_done        = "Wrote to RSS"
message_copied          = "Copied RSS text to clipboard."
message_new_file_done   = "Wrote RSS text to new file"
message_help            = [ "\n",
                            "="*34 + " HTML 2 RSS " + "="*34 + "\n",
                            "\n",
                            "What is this:\n"
                            f"\t{''.join(description)}\n",
                            "Usage: \n",
                            f"\tpython3 {__file__} <path_to_HTML_file>\n",
                            "\n",
                            "During program:\n",
                            "\tYou are asked a series of questions in this order:\n"
                            "\t1. Confirm title (keeps asking for next possible title if incorrect)\n",
                            "\t2. Confirm URL of the original post (type URL if incorrect)\n",
                            "\t3. Copy to RSS file (y/n, then confirm file. Type path if incorrect)?\n",
                            "\t4. Copy output to clipboard?\n",
                            "\t5. Copy output to new file?\n",
                            "\t6. Print output?\n",
                            "\n",
                            "Program Requirements (for now):\n",
                            "\tTitle tag must be only in one line (ex: <h1>Title</h1>)\n",
                            "\n",
                            "="*80 + "\n"]


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
    # ========= CONFIGURABLE VARIABLES =========
    url_domain          = "husseinesmail.xyz"
    url_prefix          = f"https://{url_domain}/articles/"   # Used for guessing the future URL of the post. Used for all/ compiling and RSS
    rss_author          = "Hussein Esmail"      # Used for RSS feed posts
    rss_label           = "Hussein's Articles"  # Used for RSS feed posts
    rss_term            = "Articles"            # Used for RSS feed posts
    tag_type_title      = "h1"                  # Used for RSS feed posts - Will automatically be the title tag of the RSS post
    char_placehold      = "|"                   # This character is used in determining what's inside the title tag
    rss_path            = f"/hdd1/Website/{url_domain.split('.')[0]}/rss.xml"
    rss_insert_pos      = "<!-- FEEDS START -->"    # Used for RSS feed posts - Where to insert after
    all_created_date    = "2021 05 06"          # Used for recompiling '/articles/all/index.html'
    all_file_path       = f"/hdd1/Website/{url_domain.split('.')[0]}/articles/all/index.html"
    all_file_csv        = f"/hdd1/Website/{url_domain.split('.')[0]}/articles/articles.csv"
    all_month_header    = "h2"                  # Used for all/

    # ========= VARIABLES USED BY PROGRAM =========
    str_post_title      = ""                    # Title of RSS post
    lines_all           = []                    # Unformatted HTML from the post file.
    lines_wanted        = []                    # Formatted lines will go here (after replacing escape codes)
    lines_finished      = []                    # RSS post lines will go here (and lines from lines_wanted)
    bool_end_body       = False                 # Used when reading input HTML file
    bool_out_file       = False                 # Will be True later if user chooses to copy to new file
    bool_out_rss        = False                 # Will be True later if user chooses to add to RSS file
    bool_out_copy       = False                 # Will be True later if user chooses to copy to clipboard


    if len(sys.argv) != 2:
        if len(sys.argv) < 2:
            print(f"{str_prefix_err} {error_input_html}")
        else:
            print(f"{str_prefix_err} {error_too_many_args}")
    else: # If this program received the proper number of arguments

        dev_mode = yes_or_no("Are you running in testing mode? ")
        if dev_mode:    
            # Test variables are here, replacing the real ones so this doesn't make irreversable changes
            rss_path        = os.path.expanduser(f"~/Downloads/{url_domain.split('.')[0]}/rss.xml") 
            all_file_path   = os.path.expanduser(f"~/Downloads/{url_domain.split('.')[0]}/articles/all/index.html")
            all_file_csv    = os.path.expanduser(f"~/Downloads/{url_domain.split('.')[0]}/articles/articles.csv")

        if "-h" in sys.argv[-1] or "--help" in sys.argv[-1]:
            print("".join(message_help))
        elif sys.argv[-1].lower().endswith(".html"):    # All arguments pass
            html_path = sys.argv[-1]
            lines_all = open(os.path.expanduser(html_path)).readlines()  # Read the HTML file
            # expanduser(): If user types "~" instead of home dir path
            cont = True             # Keep asking about title tag until the user verifies the title
            for position, line in enumerate(lines_all):  # For every line
                if f"<{tag_type_title}" in line.strip() and cont: # If the line includes the start of the title tag
                    # Didn't include '>' because there may be classes before the bracket
                    if f"</{tag_type_title}>" in line.strip(): # Title is definitely in this line only
                        line2 = line.replace("<", "x", 1).replace(">", char_placehold, 1).replace("<", char_placehold, 1)
                        indexes = [i for i, ltr in enumerate(line2) if ltr == char_placehold]
                        line3 = line[indexes[0]+1:indexes[-1]].strip()
                        if len(line3) > 0 and yes_or_no(f"Is this the title: '{line3}'? "):
                            str_post_title = line3      # Set selection as the post title
                            cont = False                # Do not keep asking about titles
                            int_line_start = position   # Line number of the title of the post
            if cont:
                print(f"{str_prefix_err} {error_no_title}")     # User did not select a title
                sys.exit()                  # User must restart program and select one then
            
            if html_path[0] == "." and not html_path[0].isalnum():   
                # Support for current working directory
                os.chdir(os.getcwd())
            
            for position, line in enumerate(lines_all):
                if "</body>" in line.replace(" ", "").strip(): # Check if it reached the end of the body tag, aka the end of the RSS content
                    bool_end_body = True
                if int_line_start <= position and not bool_end_body: # If it's after or on the start line number, and if it hasn't reached the end
                    # Need to replace "&" with "&amp;" first or else it will also replace the other escape codes too.
                    lines_wanted.append(line.replace("&", "&amp;").replace("'", "&apos;").replace("\"", "&quot;").replace("<", "&lt;").replace(">", "&gt;"))
            
            cont = True
            file_name = html_path.split("/")[-1]
            article_url_tmp = f"{url_prefix}{file_name}"
            cont = not yes_or_no(f"Is this correct: '{article_url_tmp}'? ")
            if not cont:
                article_url = article_url_tmp
            while cont: # Keep asking for URL until user confirms it is correct.
                article_url = input(f"{str_prefix_ques} Article URL: ")
                if not article_url.startswith("https://") or not article_url.startswith("http://"):
                    article_url = "http://" + article_url
                if validators.url(article_url):
                    cont = not yes_or_no(f"Is this correct: '{article_url}'? ")
                else:
                    print(f"{str_prefix_err} {error_invalid_url}")
            # Generate the current date and time in RSS format
            date_publish = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()

            lines_finished.append(f"\t<entry>")
            lines_finished.append(f"\t\t<title>{str_post_title}</title>")
            lines_finished.append(f"\t\t<published>{date_publish}</published>")
            lines_finished.append(f"\t\t<updated>{date_publish}</updated>")
            lines_finished.append(f"\t\t<link href=\"{article_url}\"/>")
            lines_finished.append(f"\t\t<author>")
            lines_finished.append(f"\t\t\t<name>{rss_author}</name>")
            lines_finished.append(f"\t\t</author>")
            lines_finished.append(f"\t\t<category term=\"{rss_term}\" label=\"{rss_label}\"/>")
            lines_finished.append(f"\t\t<content type=\"html\">")
            for i in lines_wanted:
                lines_finished.append(f"\t\t{i[:-1]}")
            lines_finished.append(f"\t\t</content>")
            lines_finished.append(f"\t</entry>")
            lines_finished = [line + "\n" for line in lines_finished]

            while True:
                out_rss         = yes_or_no("Add to RSS file? ")
                if out_rss:
                    if not yes_or_no(f"Is this the correct RSS file: '{rss_path}'? "):
                        rss_path = ""
                        while not os.path.exists(os.path.expanduser(rss_path)):
                            rss_path = input(f"{str_prefix_ques} What is the file path? ")
                            all_file_csv = f"{'/'.join(rss_path.split('/')[:-1])}/articles/articles.csv"
                            all_file_path = f"{'/'.join(rss_path.split('/')[:-1])}/articles/articles.csv"
                            if not os.path.exists(os.path.expanduser(rss_path)):
                                print(f"{str_prefix_err} Not a path!")
                out_clipboard   = yes_or_no("Copy output to clipboard? ")
                out_file        = yes_or_no("Copy output to new file? ")
                out_stdout      = yes_or_no("Print output here? ")
                
                if not (out_clipboard or out_file or out_stdout or out_rss):
                    print(f"{str_prefix_err} {error_no_out_choice}")
                else:
                    if out_clipboard:                                               # Copy to clipboard
                        pyperclip.copy("".join(lines_finished))                         # Copy all the lines as one string
                        bool_out_copy = True
                        
                    if out_file:                                                    # Copy to new file
                        str_file_name = os.path.expanduser(input(f"{str_prefix_ques} File name for output: "))
                        if (os.path.exists(str_file_name) and yes_or_no("File exists. Append to file? ")) or os.access(os.path.dirname(str_file_name), os.W_OK):
                            # the file does not exists but write privileges are given or file exists.
                            bool_out_file = True
                        else: # can not write there
                            print(f"{str_prefix_err} File cannot be created.")
                        if bool_out_file:
                            open(str_file_name, "a").writelines(lines_finished)             # Write to new file (append)
                            
                    if out_stdout:                                                  # Print the new lines
                        print("".join(lines_finished))
                        # Requires no notification to user that it's done (it will literally be right there).
                    if out_rss:                                                     # Add to RSS feed
                        # This is after out_stdout so that the user sees that this will be done too 
                        # (and won't have to search for the DONE message)
                        rss_lines = open(rss_path, 'r').readlines()                # Read the current RSS
                        rss_lines_strip = [line.strip() for line in rss_lines]          # Get striped lines of RSS
                        rss_insert_line_index = rss_lines_strip.index(rss_insert_pos)  # Find where the delimiter is
                        # Join the arrays: {RSS lines before delimiter + delimiter} + {new lines} + {RSS lines after delimiter}
                        rss_lines_new = rss_lines[:rss_insert_line_index+1] + lines_finished + rss_lines[rss_insert_line_index+1:]
                        open(rss_path, 'w').writelines(rss_lines_new)              # Overwrite RSS file with new lines (included all old lines)
                        bool_out_rss = True
                    break
            
            # Add to /articles/all/index.html
            # Get created date of current post
            str_post_created = ""                       # Created date of the post to add will go here.
            for line in reversed(lines_all):
                if "Created" in line and len(str_post_created) == 0:
                    str_post_created = line.replace("Created:", "").strip()[-10:] # ex. "2021 04 29"
            
            # Open CSV file and read contents. Format: Date, Title, URL
            lines_csv = list(csv.reader(open(all_file_csv)))
            article_url_relative = article_url.split(url_domain)[-1]
            lines_csv.append([str_post_created, str_post_title, article_url_relative])   # Add new post
            lines_csv[1:] = sorted(lines_csv[1:], key=operator.itemgetter(0))   # Sort by first column (ignore first row, those are the column identifiers)

            # Save CSV file
            with open(all_file_csv, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(lines_csv)
            
            # Header info for /articles/all/index.html
            lines_html = []
            lines_html.append(f'<!DOCTYPE html>\n')
            lines_html.append(f'<html lang="en-us">\n')
            lines_html.append(f'\n')
            lines_html.append(f'<head>\n')
            lines_html.append(f'\t<title>Articles</title>\n')
            lines_html.append(f'\t<link rel="stylesheet" type="text/css" href="/style.css" media="screen"/>\n')
            lines_html.append(f'\t<meta charset="utf-8">\n')
            lines_html.append(f'\t<meta name="viewport" content="width=device-width, initial-scale=1">\n')
            lines_html.append(f'\t<meta name="format-detection" content="telephone=no">\n')
            lines_html.append(f'</head>\n')
            lines_html.append(f'<body>\n')
            lines_html.append(f'\t<h1><a class="stealth-url" href="/">Hussein Esmail</a></h1>\n')
            lines_html.append(f'\t<div class="nav">\n')
            lines_html.append(f'\t\t<header>\n')
            lines_html.append(f'\t\t\t<ul class="nav-ul">\n')
            lines_html.append(f'\t\t\t\t<li><a class="stealth-url" href="/about"    title="About">About</a></li>\n')
            lines_html.append(f'\t\t\t\t<li><a class="stealth-url" href="/articles" title="Articles">Articles</a></li>\n')
            lines_html.append(f'\t\t\t\t<li><a class="stealth-url" href="/books"    title="Books">Books</a></li>\n')
            lines_html.append(f'\t\t\t\t<li><a class="stealth-url" href="/guides"   title="Theatre Guides">Theatre Guides</a></li>\n')
            lines_html.append(f'\t\t\t\t<li><a class="stealth-url" href="/rss.xml"  title="RSS">RSS</a></li>\n')
            lines_html.append(f'\t\t\t\t<li><a class="stealth-url" href="/contact"  title="Contact">Contact</a></li>\n')
            lines_html.append(f'\t\t\t</ul>\n')
            lines_html.append(f'\t\t</header>\n')
            lines_html.append(f'\t</div>\n')
            lines_html.append(f'\t<h1>All Article Posts</h1>\n')
            
            last_date    = "0000 00"
            # Split rows in CSV by month
            for line in reversed(lines_csv[1:]): # lines_csv[1:] because index 0 are the column names
                current_year = line[0].split(" ")[0]
                current_month = line[0].split(" ")[1]
                if current_year + ' ' + current_month != last_date:    # New month/year
                    if not last_date == "0000 00":            # If not first post, close the old list.
                        lines_html.append("\t</ul>\n")
                    current_month_name = datetime.datetime.strptime(current_month, "%m").strftime("%B") # Month as text
                    lines_html.append(f"\t<{all_month_header}>{current_month_name} {current_year}</{all_month_header}>\n")
                    lines_html.append("\t<ul>\n")
                lines_html.append("\t\t<li>\n")
                lines_html.append(f'\t\t\t{line[0]}: <a href="{line[2]}">{line[1]}</a>\n')
                lines_html.append("\t\t</li>\n")
                last_date = current_year + ' ' + current_month
            
            # Footer info for /articles/all/index.html
            lines_html.append("\t</ul>\n")  # At the end, close the last open list
            lines_html.append('</body>\n')
            lines_html.append('<footer>\n')
            lines_html.append('\t<br>\n')
            lines_html.append('\t<p>\n')
            lines_html.append(f'\t\tCreated: &nbsp; {all_created_date}\n')
            lines_html.append('\t</p>\n')
            lines_html.append('\t<br>\n')
            lines_html.append('\t<p>\n')
            lines_html.append(f'\t\tEdited: &nbsp; &nbsp;  {datetime.datetime.now().strftime("%Y %m %d")}\n')
            lines_html.append('\t</p>\n')
            lines_html.append('</footer>\n')
            lines_html.append('</html>\n')

            open(all_file_path, 'w').writelines(lines_html)     # Write new re-compiled version of all/
            
            # Done messages here
            if bool_out_rss:
                print(f"{str_prefix_done} {message_rss_done}")
            if bool_out_copy:
                print(f"{str_prefix_done} {message_copied}")
            if bool_out_file:
                print(f"{str_prefix_done} {message_new_file_done}")
            print(f"{str_prefix_done} Added to all/")

        else: # If a file was given but it does not have a .HTML extension
            print(f"{str_prefix_err} {error_incorrect_args}")
    sys.exit()

if __name__ == "__main__":
    main()
