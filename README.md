# html2rss
Convert an HTML page to RSS with URL support

# Table of Contents
- [What is this?](#what-is-this)
    - [Why does this help?](#Why-does-this-help)
- [Installation](#installation)
- [Requirements](#requirements)
- [Usage](#usage)
    - [Output Methods](#output-methods)

# What is this?

This program takes a simple HTML page and converts it to an RSS format where URLs are more supported.

## Why does this help?

In the terminal application [newsboat](https://github.com/newsboat/newsboat), RSS feeds that are not formatted this way does not recognize URLs as actual URLs, just text. When they are formatted this way, the URLs can be opened by uring url-view or by pressing numbers 1-9 (first link = 1, second = 2, etc). Similar to how Reddit RSS feeds look in newsboat.

# Installation

```
git clone https://github.com/hussein-esmail7/html2rss
cd html2rss/
pip install requirements.txt
```

# Requirements

To run this program, you will need to have Python 3 installed, and install the required libraries from pip (using `requirements.txt`).

# Usage 

```
python3 html2rss.py {HTML File location}
```

This program takes 1 argument, and that is the file location of the HTML file.

## Output Methods

When outputting, the program will ask if you want to copy to clipboard, save to file, or print to standard output. You can also have multiple output types or all of them.
