'''
all.py
Hussein Esmail
Created: 2022 01 03
Updated: 2022 04 14
Description: This program is meant to run all the other RSS parser programs in
    this folder. The reason this is not a .bashrc alias is because arguments
    that are parsed to this program will be carried over to all the programs
    this one runs, such as --verbose, --quiet, --version, etc.
'''

import os
import sys
import glob # Lists all files in directory with wildcard
import argparse # Parses given arguments

# ========= VARIABLES ===========
paths_exclude = [
    "rss_html.py",
    "rss_reddit_imgdl.py",
    "rss_yfile.py",
    "rss_tiktok.py",
    "rss_scaruffi.py"
] # Programs to exclude even if they meet all requirements

# rss_yfile.py: I personally don't use this file anymore
# rss_scaruffi.py: Request by someone else
# rss_workinculture.py: Work in progress

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
error_neither_y_n = "You must either type 'y' or 'n' (or 'q' to exit)"

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
    # https://www.onlinetutorialspoint.com/python/how-to-pass-command-line-arguments-in-python.html
    parser = argparse.ArgumentParser()

    # Commands to create
    parser.add_argument("-v", "--verbose", action="store_true",help="Verbose mode", dest="verbose")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode (overrides --verbose)", dest="quiet")

    args = parser.parse_args()

    if args.verbose and args.quiet:
        print(str_prefix_err + "Cannot have --verbose and --quiet. Using --quiet")
        args.verbose = False

    # Path of where this Python file is
    path_this_file = os.path.dirname(os.path.realpath(__file__))
    # Program must contain "rss" in filename and be in same folder
    programs_run = glob.glob(path_this_file + "/*rss*.py")

    # Removing excluded programs to run
    programs_run = sorted([program for program in programs_run if program.split("/")[-1] not in paths_exclude])

    args_send = " " # Arguments to send
    if args.quiet:
        if len(args_send.strip()) == 0:
            args_send += "-"
        args_send += "q"
    elif args.verbose:
        if len(args_send.strip()) == 0:
            args_send += "-"
        args_send += "v"

    for program_run in programs_run:
        if not args.quiet:
            print("="*6 + " "*3 + "="*20)
            print(str_prefix_info + "Running " + program_run.split("/")[-1] + args_send)
        os.system("python3 " + program_run + args_send)

    sys.exit()

if __name__ == "__main__":
    main()
