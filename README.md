# rss_parsers
A collection of Python scripts that converts pages to RSS.

## Table of Contents
- [What is this?](#what-is-this)
    - [Why does this help?](#Why-does-this-help)
- [List of Files](#list-of-files)
- [Installation](#installation)
- [to_rss.py](#to_rss.py)
- [Usage (per program)](#usage)
	- [rss_html.py](#rss_html.py)
  - [rss_pact.py](#rss_pact.py)
	- [rss_reddit_imgdl.py](#rss_reddit_imgdl.py)
  - [rss_tapa.py](#rss_tapa.py)
	- [rss_tiktok.py](#rss_tiktok.py)
	- [rss_vsco.py](#rss_vsco.py)
  - [rss_workinculture.py](#rss_workinculture.py)
	- [rss_yfile.py](#rss_yfile.py)
- [Donate](#donate)

## What is this?
This program takes a simple HTML page and converts it to an RSS format where
URLs are more supported.

### Why does this help?
In the terminal application [newsboat](https://github.com/newsboat/newsboat),
RSS feeds that are not formatted this way does not recognize URLs as actual
URLs, just text. When they are formatted this way, the URLs can be opened by
uring url-view or by pressing numbers 1-9 (first link = 1, second = 2, etc).
Similar to how Reddit RSS feeds look in newsboat. In other cases, some RSS feed
providers don't provide as much content in their feeds as they do in their web
pages. Programs in this repository rectify both of these issues.

## List of Files
- [rss_booksalefinder.py](blob/main/rss_booksalefinder.py): TODO -----
- [rss_citt.py](blob/main/rss_citt.py): TODO -----
- [rss_html.py](blob/main/rss_html.py): Convert a local HTML file to RSS.
  Intended for my own website, [husseinesmail.xyz](https://husseinesmail.xyz)
  but can be manipulated to work with other sites.
- [rss_pact.py](blob/main/rss_pact.py): TODO -----
- [rss_reddit_imgdl.py](blob/main/rss_reddit_imgdl.py): Takes an RSS feed from
  Reddit and downloads all images from the https://i.redd.it/ domain so they
  can be viewed from [newsboat](https://newsboat.org) offline.
  [r/unixporn](https://reddit.com/r/unixporn) is a good example of how this
  program can be used. *Note: I haven't been using this one recently.*
- [rss_tapa.py](blob/main/rss_tapa.py): TODO -----
- [rss_tiktok.py](blob/main/rss_tiktok.py): This uses Selenium to scrape the
  top posts of a person's TikTok profile and appends them to a RSS feed.
- [rss_vsco.py](blob/main/rss_vsco.py): Gets post URLs along with URLs to the
  images directly of a VSCO page using just the username in the `urls` file.
  This looks at the first loaded posts on a page, so it won't load all of them,
  just the most recent ones (usually the top 45).
- [rss_workinculture.py](blob/main/rss_workinculture.py): TODO -----
- [rss_yfile.py](blob/main/rss_yfile.py): YFile newsletter at York University.
  They do have an RSS feed, but their RSS posts are only a fraction of what is
  displayed on each YFile article page. That annoyed me, so I thought to myself
  "Fine, I'll do it myself" (-Thanos). *Note: I've been using
  [https://morss.it/https://yfile.news.yorku.ca/feed/atom/](https://morss.it/https://yfile.news.yorku.ca/feed/atom/)
  instead of this program recently and it's been working well.*

## Installation
```
git clone https://github.com/hussein-esmail7/rss_parsers
cd rss_parsers/
pip install requirements.txt
```

## to_rss.py
This file is an abstraction that contains the functions to manage RSS files.
```
create_rss(path: str, title: str, subtitle: str)
```
Creates the RSS file at the given path, and parent folders if needed. If the file exists, do nothing.
```
check_post_exists(path: str, url: str, guid: str)
```
Returns boolean value. Input the RSS file path, as well as URL and GUID of the post you want to check. If the GUID is given an empty string (i.e. `""`), it uses the URL as a fallback.
```
add_to_rss(path: str, title: str, author: str, date: str, url: str, guid: str, body: str)
```
Adds post to RSS file. If the post already exists (using `check_post_exists()`), do nothing.

## Usage

### rss_html.py
```
python3 rss_html.py {HTML File location}
```
This program takes 1 argument, and that is the file location of the HTML file.
When outputting, the program will ask if you want to copy to clipboard, save to
file, or print to standard output. You can also have multiple output types or
all of them.

### rss_pact.py
```
python3 rss_pact.py
```
This program takes no arguments. It generates an RSS feed of the top page of the Professional Association of Canadian Theatres job posting page.

### rss_reddit_imgdl.py
```
python3 rss_reddit_imgdl.py
```
This program takes no arguments, though it will take a urls file, and those
URLs should be Reddit RSS feeds. If there is no urls file, it will ask you for
a URL before running.

### rss_tapa.py
```
python3 rss_tapa.py
```
This program takes no arguments. It generates an RSS feed of the top page of the Toronto Alliance for the Performing Arts job posting page.

### rss_tiktok.py
```
python3 rss_tiktok.py
```
This program takes no arguments, but requires a few things to be set up in the
program.  It requires a urls file in the file path that is set in the
`TIKTOK_URLS` variable, and all folders in the user-configurable variables
section must exist. This program uses Selenium to scrape each URL given, and at
the moment must not be run in the background as some of the webpage loading
required JavaScript. If anyone has a solution to this, please feel free to
submit a pull request.

### rss_vsco.py
```
python3 rss_vsco.py
```
This program takes no arguments, but there are variables that you can configure
at the beginning of the file (ex. RSS file location). This program will only
output to a local RSS feed at the set location (in variable `RSS_FOLDER`). This
currently does not work on Windows, because I have no Windows machine to test
it on. Pull requests with a tested version are welcome.

### rss_workinculture.py
```
python3 rss_workinculture.py
```
This program takes no arguments. It generates an RSS feed of the top page of the Work In Culture job posting page.

### rss_yfile.py
```
python3 rss_yfile.py
```
This program takes no arguments, but there are variables that you can configure
at the beginning of the file (ex. RSS file location). This program will only
output to a local RSS feed at the set location (in variable `RSS_FOLDER`).

## Donate
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/husseinesmail)
