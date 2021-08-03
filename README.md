# rss_parsers
A collection of Python scripts that converts pages to RSS.

## Table of Contents
- [What is this?](#what-is-this)
    - [Why does this help?](#Why-does-this-help)
- [List of Files](#list-of-files)
- [Installation](#installation)
- [Usage (per program)](#usage)
- [Donate](#donate)

## What is this?
This program takes a simple HTML page and converts it to an RSS format where URLs are more supported.

### Why does this help?
In the terminal application [newsboat](https://github.com/newsboat/newsboat), RSS feeds that are not formatted this way does not recognize URLs as actual URLs, just text. When they are formatted this way, the URLs can be opened by uring url-view or by pressing numbers 1-9 (first link = 1, second = 2, etc). Similar to how Reddit RSS feeds look in newsboat. In other cases, some RSS feed providers don't provide as much content in their feeds as they do in their web pages. Programs in this repository rectify both of these issues.

## List of Files
- [rss_html.py](blob/main/rss_html.py): Convert a local HTML file to RSS. Intended for my own website, [husseinesmail.xyz](https://husseinesmail.xyz) but can be manipulated to work with other sites.
- [rss_yfile.py](blob/main/rss_yfile.py): YFile newsletter at York University. They do have an RSS feed, but their RSS posts are only a fraction of what is displayed on each YFile article page. That annoyed me, so I thought to myself "Fine, I'll do it myself" (-Thanos).

## Installation
```
git clone https://github.com/hussein-esmail7/rss_parsers
cd rss_parsers/
pip install requirements.txt
```

## Usage 

### rss_html.py
```
python3 rss_html.py {HTML File location}
```
This program takes 1 argument, and that is the file location of the HTML file. When outputting, the program will ask if you want to copy to clipboard, save to file, or print to standard output. You can also have multiple output types or all of them.

### rss_yfile.py
```
python3 rss_yfile.py
```
This program takes no arguments, but there are variables that you can configure at the beginning of the file (ex. RSS file location). This program will only output to a local RSS feed at the set location (in variable `RSS_FOLDER`).

## Donate
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/husseinesmail)