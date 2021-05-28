'''
html2rss.py by  Hussein Esmail
Created: 2021 05 05
Updated: 2021 05 10
Description: This inputs an HTML file in the arguments and converts a copy of it to an RSS format where in-item URLs are supported in Newsboat (like on Reddit RSS pages, because if I prefer them then someone else probably does too).
'''
import os, sys
import datetime
import pyperclip

def yes_or_no(str_ask):
    while True:
        y_n = input(str_ask).lower()
        if y_n[0] == "y":
            return True
        elif y_n[0] == "n":
            return False
        else:
            print("The first character must either be a 'y' or 'n'.")

def main():
    author = "Hussein Esmail"
    label = "Hussein's Articles"
    term = "Articles"
    str_post_title = ""

    message_input_html = "You need to input an HTML file to convert!"
    message_too_many_args = "You typed more arguments than I expected. Please verify and try again."
    message_not_an_int = "I didn't like that input! Please type an int."
    message_incorrect_args = "I don't know what you gave me... but it wasn't an HTML file."
    message_copied = "Copied to clipboard."

    lines_wanted = []
    lines_finished = []

    int_reached_end_of_body_tag = 0

    tag_type_title = "h1"

    if len(sys.argv) != 2:
        if len(sys.argv) < 2:
            print(message_input_html)
        else:
            print(message_too_many_args)
    else: # If this program received the proper number of arguments
        if sys.argv[-1].lower().endswith(".html"):
            lines_all = open(sys.argv[-1]).readlines()

            for line in lines_all:
                if f"<{tag_type_title}" in line.strip(): 
                    # Didn't include '>' because there may be classes before the bracket
                    if f"</{tag_type_title}>" in line.strip(): 
                        # Title is definitely in this line only
                        
                        str_post_title = line[line.find("&gt;")+4:line.replace("&lt;", "XXXX", 1).find("&lt;")].strip()
                    else:
                        print("TODO")





            while True: # Ask for the line number of where to start converting (as int)
                int_line_start = input(f"First line of the post (h1 tag with the title) [/{len(lines_all)} lines]? ")
                try:
                    int_line_start = int(int_line_start) - 1 
                    # -1 beacuse it won't read the line number provided otherwise, it would start at the next line 
                    # (tl;dr: arrays start at 0)
                    break
                except:
                    print(message_not_an_int)
                    pass

            
            if sys.argv[-1].startswith("./"): # Support for current working directory
                os.chdir(os.getcwd())
            elif sys.argv[-1].startswith("~"):  # Support for home directory
                os.chdir(os.path.expanduser("~"))
            
            for position, line in enumerate(lines_all):
                if "</body>" in line.replace(" ", ""): # Check if it reached the end of the body tag, aka the end of the RSS content
                    int_reached_end_of_body_tag = 1 
                if int_line_start <= position and int_reached_end_of_body_tag == 0: # If it's after or on the start line number, and if it hasn't reached the end
                    # Need to replace "&" with "&amp;" first or else it will also replace the other escape codes too.
                    lines_wanted.append(line.replace("&", "&amp;").replace("'", "&apos;").replace("\"", "&quot;").replace("<", "&lt;").replace(">", "&gt;"))
            # At this point, lines_wanted has all the formatted RSS-friendly HTML lines we want, with \n at the end of each line.
            # Check for the post title:
            cont = True
            for line in lines_wanted:
                if "&lt;" + tag_type_title in line.replace(" ", "") and cont:
                    str_post_title = line[line.find("&gt;")+4:line.replace("&lt;", "XXXX", 1).find("&lt;")].strip()
                    is_title = yes_or_no(f"Is this the post title: \"{str_post_title}\" [y/n]? ")
                    if is_title:
                        cont = False
            
            cont = True
            while cont: # Keep asking for URL until user confirms it is correct.
                article_url = input("Article URL: ")
                cont = not yes_or_no(f"Is this correct: {article_url} [y/n]: ")
            
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
            
            while True:
                out_clipboard = yes_or_no("Copy to clipboard [y/n]? ")
                out_file = yes_or_no("Copy to file [y/n]? ")
                out_stdout = yes_or_no("Print output [y/n]? ")
                if not (out_clipboard or out_file or out_stdout):
                    print("You gotta pick something, dude.")
                else:
                    if out_clipboard:
                        pyperclip.copy("\n".join(lines_finished))
                        print(message_copied)
                    if out_file:
                        str_file_name = input("File name for output: ")
                        with open(str_file_name, "a") as output_file:
                            for line in lines_finished:
                                output_file.write(f"{line}\n")
                        print(f"Wrote to '{str_file_name}'")
                    if out_stdout:
                        print("\n".join(lines_finished))
                    break
        else: # If a file was given but it does not have a .HTML extension
            print(message_incorrect_args)
    sys.exit()


if __name__ == "__main__":
    main()
