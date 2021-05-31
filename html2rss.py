'''
html2rss.py by  Hussein Esmail
Created: 2021 05 05
Updated: 2021 05 28
'''
description = [ "This inputs an HTML file in the arguments and converts a copy of it to\n",
                "an RSS format where in-item URLs are supported in Newsboat (like on \n",
                "Reddit RSS pages, because if I prefer them then someone else probably\n",
                "does too).\n"]

import os, sys
import datetime
import pyperclip
import validators
import re

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
message_copied          = "Copied to clipboard."
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
        else:
            print(f"{str_prefix_err} {error_neither_y_n}")

def main():
    print("TODO: Program started")
    # ========= CONFIGURABLE VARIABLES =========
    author = "Hussein Esmail"
    label = "Hussein's Articles"
    term = "Articles"
    tag_type_title = "h1"   # Will automatically be the title tag of the RSS post
    char_placehold = "|"    # This character is used in determining what's inside the title tag
    
    auto_url = True         # Automatically guess URL to the post (user can still change when running)
    auto_url_template = "https://husseinesmail.xyz/articles/"   # + {HTML page}
    # auto_rss_path = "/hdd1/Backups/Website/husseinesmail/rss.xml"     # TODO: Real one
    auto_rss_path = os.path.expanduser("~/Downloads/husseinesmail/rss.xml")   # TODO: Test string (so I don't mess with the site)
    auto_rss_insert = "<!-- FEEDS START -->"

    # Used to automatically add post to all/index.html
    # auto_add_all_posts_path = "/hdd1/Backups/Website/husseinesmail/articles/all/index.html"
    auto_add_all_posts_path = os.path.expanduser("~/Downloads/husseinesmail/articles/all/index.html")   # TODO: Test string (so I don't mess with the site)
    auto_add_all_posts_header_tag = "h2"
    auto_add_all_posts_header_line      = -1 # Header line of the month in the all/ file.
    auto_add_all_posts_header_line_next = -1 # Header line of the next month in the all/ file (aka the end of the block we want to edit)
    auto_add_all_posts_list_tag = "<li>"

    # ========= VARIABLES USED BY PROGRAM =========
    int_reached_end_of_body_tag = 0
    str_post_title  = ""    # Used later, must be in this scope
    lines_all       = []    # Unformatted HTML from the post file.
    lines_wanted    = []    # Formatted lines will go here (after replacing escape codes)
    lines_finished  = []    # RSS post lines will go here (and lines from lines_wanted)

    if len(sys.argv) != 2:
        if len(sys.argv) < 2:
            print(f"{str_prefix_err} {error_input_html}")
        else:
            print(f"{str_prefix_err} {error_too_many_args}")
    else: # If this program received the proper number of arguments
        if "-h" in sys.argv[-1] or "--help" in sys.argv[-1]:
            print("".join(message_help))
        elif sys.argv[-1].lower().endswith(".html"):
            print("TODO: Confirmed HTML file")
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
                            # print(f"Title set as: {str_post_title}")
            if cont:
                print(f"{str_prefix_err} {error_no_title}")     # User did not select a title
                sys.exit()                  # User must restart program and select one then
            
            if html_path[0] == "." and not html_path[0].isalnum():   
                # Support for current working directory
                os.chdir(os.getcwd())
            
            for position, line in enumerate(lines_all):
                if "</body>" in line.replace(" ", "").strip(): # Check if it reached the end of the body tag, aka the end of the RSS content
                    int_reached_end_of_body_tag = 1 
                if int_line_start <= position and int_reached_end_of_body_tag == 0: # If it's after or on the start line number, and if it hasn't reached the end
                    # Need to replace "&" with "&amp;" first or else it will also replace the other escape codes too.
                    lines_wanted.append(line.replace("&", "&amp;").replace("'", "&apos;").replace("\"", "&quot;").replace("<", "&lt;").replace(">", "&gt;"))
            
            cont = True
            if auto_url:
                file_name = html_path.split("/")[-1]
                article_url_tmp = f"{auto_url_template}{file_name}"
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
            lines_finished.append(f"\t\t\t<name>{author}</name>")
            lines_finished.append(f"\t\t</author>")
            lines_finished.append(f"\t\t<category term=\"{term}\" label=\"{label}\"/>")
            lines_finished.append(f"\t\t<content type=\"html\">")
            for i in lines_wanted:
                lines_finished.append(f"\t\t{i[:-1]}")
            lines_finished.append(f"\t\t</content>")
            lines_finished.append(f"\t</entry>")
            lines_finished = [line + "\n" for line in lines_finished]

            while True:
                out_rss         = yes_or_no("Add to RSS file? ")
                out_clipboard   = yes_or_no("Copy output to clipboard? ")
                out_file        = yes_or_no("Copy output to new file? ")
                out_stdout      = yes_or_no("Print output here? ")
                if out_rss:
                    if not yes_or_no(f"Is this the correct RSS file: '{auto_rss_path}'? "):
                        auto_rss_path = ""
                        while not os.path.exists(os.path.expanduser(auto_rss_path)):
                            auto_rss_path = input(f"{str_prefix_ques} What is the file path? ")
                            if not os.path.exists(os.path.expanduser(auto_rss_path)):
                                print(f"{str_prefix_err} Not a path!")
                if not (out_clipboard or out_file or out_stdout or out_rss):
                    print(f"{str_prefix_err} {error_no_out_choice}")
                else:
                    if out_clipboard:                                               # Copy to clipboard
                        pyperclip.copy("".join(lines_finished))                         # Copy all the lines as one string
                        print(f"{str_prefix_done} {message_copied}")                    # Inform user that it's done
                    if out_file:                                                    # Copy to new file
                        str_file_name = input(f"{str_prefix_ques} File name for output: ")
                        open(str_file_name, "a").writelines(lines_finished)             # Write to new file (append)
                        print(f"{str_prefix_done} Wrote to '{str_file_name}'")          # Inform user that it's done
                    if out_stdout:                                                  # Print the new lines
                        print("".join(lines_finished))
                        # Requires no notification to user that it's done (it will literally be right there).
                    if out_rss:                                                     # Add to RSS feed
                        # This is after out_stdout so that the user sees that this will be done too 
                        # (and won't have to search for the DONE message)
                        rss_lines = open(auto_rss_path, 'r').readlines()                # Read the current RSS
                        rss_lines_strip = [line.strip() for line in rss_lines]          # Get striped lines of RSS
                        rss_insert_line_index = rss_lines_strip.index(auto_rss_insert)  # Find where the delimiter is
                        # Join the arrays: {RSS lines before delimiter + delimiter} + {new lines} + {RSS lines after delimiter}
                        rss_lines_new = rss_lines[:rss_insert_line_index+1] + lines_finished + rss_lines[rss_insert_line_index+1:]
                        open(auto_rss_path, 'w').writelines(rss_lines_new)              # Overwrite RSS file with new lines (included all old lines)
                        print(f"{str_prefix_done} Wrote to '{auto_rss_path}'")          # Inform user that it's done
                    break
            auto_add_all_posts = yes_or_no("Append post to 'all/'? ")
            if auto_add_all_posts:
                # TODO: Not Done
                # Get created date for the post in question
                # Read all/index.html page
                # From all/, navigate to the month tag (h2)
                # In that list, figure out which position the new <li> should be
                # Insert it there, and write to all/, and change the edited date at the bottom (if there is any)

                """
                Things to fix about the insert text
                - There are no line breaks
                - tab on first <ul>
                - <ul> missing >
                - Enter + tab after <ul>
                - Enter + tab after <li>
                - Enter + tab after </li>
                - Enter + tab after </ul>
                """

                str_post_created = ""   # Created date of the post to add will go here.
                for line in reversed(lines_all):
                    if "Created" in line and len(str_post_created) == 0:
                        str_post_created = line.strip().split(" ")[-3:] # ex. ["2021", "04", "29"]

                # Line to add somewhere in the middle
                line_add_all_line_new = ["\t\t<li>\n", 
                                            f"\t\t\t{' '.join(str_post_created)}: <a href=\"../{article_url.split('/')[-1]}\">{str_post_title}</a>\n", 
                                            "\t\t</li>\n"]

                date_header_format = datetime.date(int(str_post_created[0]), int(str_post_created[1]), int(str_post_created[2])).strftime('%B %Y')
                lines_all_file_original = open(auto_add_all_posts_path, 'r').readlines()
                # print(f"Looking for: '<{auto_add_all_posts_header_tag}>{date_header_format}</{auto_add_all_posts_header_tag}>'")
                bool_found_current_month    = False
                bool_found_next_month       = False
                for position, line in enumerate(lines_all_file_original):
                    # Look for the line where it indicates the proper month.
                    if bool_found_current_month and not bool_found_next_month and (auto_add_all_posts_header_tag in line.strip() or "</body>" in line.strip()):
                        # print(f"Line {position}: '{line.strip()}'")
                        bool_found_next_month = True
                        auto_add_all_posts_header_line_next = position + 1
                    if not bool_found_current_month and f"<{auto_add_all_posts_header_tag}>{date_header_format}</{auto_add_all_posts_header_tag}>" in line.strip():
                        print(f"'<{auto_add_all_posts_header_tag}>{date_header_format}</{auto_add_all_posts_header_tag}>' is on line {position}")
                        auto_add_all_posts_header_line = position + 1
                        bool_found_current_month = True
                if auto_add_all_posts_header_line == -1:
                    # That specific month doesn't exist, add it here
                    # TODO: For now assume it doesn't work
                    print("Current month not found - NOT DONE")
                else:
                    # if the specific month is found, find the place in the <ul> it belongs (in order), and place it there

                    # The lines in the month section that we want to edit (as array)
                    lines_add_all_post_in_month = lines_all_file_original[auto_add_all_posts_header_line:auto_add_all_posts_header_line_next]

                    # The lines in the month section that we want to edit (as string)
                    lines_add_all_post_in_month_str = "".join(lines_add_all_post_in_month)

                    # print(f"lines_all_file_original[{auto_add_all_posts_header_line}:{auto_add_all_posts_header_line_next}] below:")
                    # print(f"Length: {len(lines_add_all_post_in_month_str)}")
                    # print(lines_add_all_post_in_month_str)
                    
                    # Indexes from the string <li>, to find where each date is in the list already
                    """
                    TODO: Issue - When the lines are formatted as:
                    s
                    <li>
                        2021 04 29: ---
                    </li>,

                    it doesn't recognize the date in the re.--- because it looks 10 characters 
                    until after <li> but that's just tabs because of the next line spaces.
                    It does work when it is like this:

                    <li>2021 04 29: ---
                    </li>, 

                    because it is on the same line and no spaces between
                    """
                    matches = re.finditer(auto_add_all_posts_list_tag, lines_add_all_post_in_month_str)
                    matches_positions = [match.start() for match in matches]

                    # print(f"Matches index for '{auto_add_all_posts_list_tag}': {matches_positions}")
                    # print(f"Match 1: {lines_add_all_post_in_month_str[matches_positions[0]:matches_positions[0]+10]}")

                    # This loop determine between which two lines to put the new line
                    bool_found_date_position = False
                    for match in matches_positions:
                        # For every <li> (index is at the '<')
                        # Find the dates that are in each of these <li>
                        # If the found date is later, check the one after, if it is before or no more, add there.
                        date_in_question = lines_add_all_post_in_month_str[match+len(auto_add_all_posts_list_tag):match+len(auto_add_all_posts_list_tag)+10].strip()
                        if not bool_found_date_position and len(date_in_question) > 0:
                            print(f"Date: '{date_in_question}'")
                            if date_in_question < " ".join(str_post_created):   # If the examined line is after the date of the post we want to add
                                # add the new line before this
                                # print(f"{date_in_question} is after {' '.join(str_post_created)}")

                                # Text after the new post:
                                text_after = lines_add_all_post_in_month_str[match:]
                                # text_after = "\t\t<li>\n\t\t\t".join(text_after.split("<li>", 1))
                                # text_after = "\n\t\t</li>\n\t".join(text_after.split("</li>", 1))
                                # text_after = "\n\t<h2>".join(text_after.split("<h2>", 1))
                                # text_after = "</h2>\n".join(text_after.split("</h2>", 1))

                                lines_add_all_post_in_month_str =  '\t<ul>\n'.join(lines_add_all_post_in_month_str[:match].rsplit("<ul>", 1)) + ''.join(line_add_all_line_new) + text_after
                                
                                bool_found_date_position = True
                            elif date_in_question >= " ".join(str_post_created):
                                # If the examined line is before the date of the post we want to add (most cases)
                                print("NOT DONE")
                            # If it is earlier or the same date, do nothing and go to next pos
                        elif len(date_in_question) == 0:
                            print("Empty date found.")
                            print(f"bool_found_date_position: {bool_found_date_position}")
                    
                    # Convert the one-line HTML back to formatted HTML (with tabs and new lines)
                    # lines_add_all_post_in_month_str.replace(auto_add_all_posts_header_tag, f"\t{auto_add_all_posts_header_tag}").replace(f"{auto_add_all_posts_list_tag[0]}/{auto_add_all_posts_list_tag[1:]}", f"{auto_add_all_posts_list_tag[0]}/{auto_add_all_posts_list_tag[1:]}\n").replace(auto_add_all_posts_list_tag, f"\t\t{auto_add_all_posts_list_tag}").replace("</ul>", "\t</ul>\n").replace("<ul>", "\t<ul>\n")

                    # This doesn't work because adding to '\n' to each of a string is 1 char /line
                    # lines_add_all_post_in_month_str = [line + "\n" for line in lines_add_all_post_in_month_str] # Add "\n" at the end of each line

                    lines_all_file_new = lines_all_file_original[:auto_add_all_posts_header_line] 
                    lines_all_file_new += lines_add_all_post_in_month_str 
                    lines_all_file_new += lines_all_file_original[auto_add_all_posts_header_line_next:]
                    
                    # Write to file
                    open(auto_add_all_posts_path, 'w').writelines(lines_all_file_new)

                    # Inform user that it's done
                    print(f"{str_prefix_done} Added to all/")


        else: # If a file was given but it does not have a .HTML extension
            print(f"{str_prefix_err} {error_incorrect_args}")
    sys.exit()


if __name__ == "__main__":
    main()
