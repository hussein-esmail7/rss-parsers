'''
rss_pact.py
Hussein Esmail
Created: 2024 05 20 (Mon)
Updated: 2024 05 22 (Wed)
Description: A program that converts theatre job postings to RSS feeds by city 
    (mainly focused on Toronto).
'''

import sys # To exit the program
from selenium import webdriver 
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service # Used to set Chrome location
from selenium.webdriver.chrome.options import Options # Used to add aditional settings (ex. run in background)
from selenium.webdriver.common.by import By # Used to determine type to search for (normally By.XPATH)
import datetime
import to_rss # Python function file in same directory

# ========= VARIABLES ===========
bool_run_in_background  = True # Hide selenium Chrome window

def main():
    now = datetime.datetime.now().isoformat()
    rss_path = "~/.config/rss-parsers/PACT/pact.xml"
    url = "https://www.pact.ca/artsboard" # URL to look at job posting list for
    to_rss.create_rss(path=rss_path, title="PACT Job Postings", subtitle="Professional Association of Canadian Theatres Job Postings")
    options = Options()
    if bool_run_in_background:
        options.add_argument("--headless")  # Adds the argument that hides the window
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(200, 1000) # Window size
    driver.get(url)
    elements = driver.find_elements(By.XPATH, "/html/body/main/div[2]/div[1]/div") # The list of job posting elements

    # Results from the first page will go here
    # This is needed because afterwards the program will 
    # go to the individual URLs of the posts that aren't added yet
    dict_posting_page = []

    for post in elements: # Per job post on the main page
        company = post.find_element(By.XPATH, "./div[2]/p[2]/strong").text.strip()
        dict_posting_page.append({
            'url': post.find_element(By.XPATH, "./div[4]/a").get_attribute("href"),
            'title': post.find_element(By.XPATH, "./div[2]/p[1]/a").text,
            'company': company,
            'city': post.find_element(By.XPATH, "./div[2]/p[2]").text.strip().removeprefix(company).strip(),
            'time': "",
            'closes': post.find_element(By.XPATH, "./div[3]/p[3]").text.removeprefix("Closes: ").strip(),
            'type': post.find_element(By.XPATH, "./div[3]/p[1]").text.strip(), # Part Time, Contract, etc.
            'body': ""
        })

        time_tmp = post.find_element(By.XPATH, "./div[3]/p[2]").text.removeprefix("Posted").strip().split()
        post_time = datetime.datetime.now()
        if time_tmp[1].lower() in ["hour", "hours"]:
            post_time -= datetime.timedelta(hours=int(time_tmp[0]))
        elif time_tmp[1].lower() in ["day", "days"]:
            post_time -= datetime.timedelta(days=int(time_tmp[0]))
        elif time_tmp[1].lower() in ["month", "months"]:
            post_time -= datetime.timedelta(months=int(time_tmp[0]))
        elif time_tmp[1].lower() in ["year", "years"]:
            post_time -= datetime.timedelta(years=int(time_tmp[0]))
        else:
            time_tmp_str = " ".join(time_tmp)
            print(f"ERROR! Unknown date format: {time_tmp_str}. Set date to today as fallback")
        dict_posting_page[-1]['time'] = post_time.isoformat()

    int_new_posts = 0
    for post in dict_posting_page:
        if not to_rss.check_post_exists(rss_path, url=post['url'], guid=""):
            # If post does not already exist, get the information that would take more time to get
            driver.get(post['url'])
            salary = driver.find_element(By.XPATH, "/html/body/main/div[3]/div[2]/ul/li[2]").text.replace("Salary:", "").strip()
            # term = driver.find_element(By.XPATH, "").text.strip() # Start/end dates
            job_description = driver.find_element(By.XPATH, "/html/body/main/div[4]").text.strip()
            post['body'] = f"City: {post['city']}\nSalary: {salary}\n\n{job_description}"
            to_rss.add_to_rss(path=rss_path, title=post['title'], author=post['company'], date=post['time'], url=post['url'], guid="", body=post['body'])
            int_new_posts += 1
    print(f"{int_new_posts} new posts")
    # TODO: Add from actual individual URL: Term (start-end dates)
    # TODO: Add from actual individual URL: Remote/hybrid/in-person
    driver.close() 
    options.extensions.clear() # Clear the options that were set
    sys.exit()


if __name__ == "__main__":
    main()