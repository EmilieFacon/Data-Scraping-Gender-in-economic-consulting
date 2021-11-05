## 04 Import Frontier Economics

##---------------------------------------------------
## Table of contents
## 1. Set up 
## 2. Extract list of all experts
## 3. Extract information from individual expert page
## 4. Export data set
##---------------------------------------------------

##---------------------------------------------------
## 1. Set up 
##---------------------------------------------------

# 1.1. Import libraries

import os
import re
import string
import codecs
import PyPDF2
import pandas as pd 

from requests import get
from bs4 import BeautifulSoup


# 1.2. Set up path 

path = "D:\\OneDrive\\CODE\\PROJECTS\\Data-Scraping-Gender-in-economic-consulting-firms"
os.chdir(path)

cache = path + "\\07 Cache\\04 Frontier Economics"
if not os.path.exists(cache):
    os.makedirs(cache)

    
# 1.3. Import programs and today's date

programs = path + "\\02 Scripts\\01 Import\\00 Import programs.py"
exec(open(programs).read())


# 1.4. Prepare variables which affect requests/cache

make_requests = False # If True: makes the requests on the internet
date_request = "04-11-2021" # Change this if date request is not the same as today's date


##---------------------------------------------------
## 2. Extract list of all experts
##---------------------------------------------------

## 2.0. Import page 1 and count total number of pages (26 pages)

if make_requests:
    
    all_url = "https://www.frontier-economics.com/uk/en/about/people/?page=1"
    all_request = get(all_url)
    all_html = all_request.text  
    all_soup = BeautifulSoup(all_html, 'html.parser')    
    pagination_span = all_soup.select("a.js-pagination-number span.custom-pagination-number")
    total_pages = int(pagination_span[-1].text)

else:
    
    total_pages = 26
        
    
## 2.1. Import html file and save

if make_requests:

    for i in range(1, total_pages + 1):
        
        all_url = "https://www.frontier-economics.com/uk/en/about/people/?page=" + str(i)
        all_request = get(all_url)
        
        html_filename = cache + "\\Experts page " + str(i) + " " + today + ".html"
        with open(html_filename, 'wb') as f:
                f.write(all_request.content)
                f.close()


## 2.2. Prepare list of experts

experts_link = {}
experts_role = {}


## 2.3. For each page, import cache version and get list of experts

for i in range(1, total_pages + 1):

    all_file = cache + "\\Experts page " + str(i) + " " + date_request + ".html"
    all_html = codecs.open(all_file, 'r')
    all_soup = BeautifulSoup(all_html, 'html.parser')

    wrappers = all_soup.select("a.person-item")
    
    for wrapper in wrappers:
            
        name = wrapper.select_one("h2.person-item-name").text
        name = clean_string(name)
    
        link = wrapper["href"]
        experts_link[name] = "https://www.frontier-economics.com" + link
        
        role = wrapper.select_one("h3.person-item-role").text
        experts_role[name] = role


##---------------------------------------------------
## 3. Extract information from individual expert page
##---------------------------------------------------

# 3.1. Get the expert pages and save 

if make_requests:

    cache_expert = cache + "\\Experts " + today
    if not os.path.exists(cache_expert):
        os.makedirs(cache_expert)
        
    for name, link in experts_link.items():
    
        indiv_request = get(link)
        indiv_filename = cache_expert + "\\" + name + ".html"
        with open(indiv_filename, 'wb') as f:
            f.write(indiv_request.content)
            f.close()


# 3.2. Import cache version and extract information

experts_bio = {} # Biography (text)

indiv_path = cache + "\\Experts " + date_request

for name, link in experts_link.items():
    
    # Import cache version of the expert's page 
    indiv_filename = indiv_path + "\\" + name + ".html"
    indiv_html = codecs.open(indiv_filename, 'r')
    indiv_soup = BeautifulSoup(indiv_html, 'html.parser')
    
    # Check name is the same
    name_temp = indiv_soup.select_one("h2.person-profile-banner-name").text
    name_temp = clean_string(name_temp)
    assert name == name_temp
    
    # Check role is the same
    role_temp = indiv_soup.select_one("h1.person-profile-banner-title").text
    assert role_temp == experts_role[name]
        
    # Biography
    bio_list = indiv_soup.select("div.grid-padding-x div.medium-14 p") + indiv_soup.select("div.grid-padding-x div.medium-14 div")
    bio = " ".join([bio_list[i].text for i in range(len(bio_list))])
    bio = clean_string(bio)
    experts_bio[name] = bio
    

# 3.3. Get pronouns from biography

experts_pronoun = {}

for name, bio in experts_bio.items():
 
    bio = bio.lower()

    she = bool(re.search("\sshe\s", bio)) or bool(re.search("\sher\s", bio)) 
    he = bool(re.search("\she\s", bio)) or bool(re.search("\shis\s", bio)) 
    they = bool(re.search("\sthey\s", bio))

    # Manual checks to biographies which do not pass the asserts

    if name == "Catherine Etienne":
        she = True # based on name and picture

    if name == "Hamish Forsyth":
        he = True # based on name and picture

    if name == "Freddie Harrington":
        he = True # based on name and picture
      
    if name == "Damien O'Flaherty":
        he = True # based on name and picture
                
    if name == "Maria Paula Torres":
        she = True # based on name and picture
    
    if name == "Pauline Bertino":
        they = False # refer to clients

    if name == "André Pfannenschmidt":
        they = False # refer to clients
        
    if name != "Theres Lessing": # Only person with "they" pronoun
        assert she != he
        assert they == False
    
    if she == True:
        experts_pronoun[name] = "she"
    
    elif he == True:
        experts_pronoun[name] = "he"
    
    elif they == True:
        experts_pronoun[name] = "they"


##---------------------------------------------------
## 4. Export data set
##---------------------------------------------------

# 4.1. Create multiple dataframes for merge

temp1 = pd.DataFrame.from_dict(experts_pronoun, orient='index')
temp2 = pd.DataFrame.from_dict(experts_role, orient='index')
temp3 = pd.DataFrame.from_dict(experts_link, orient='index')
temp4 = pd.DataFrame.from_dict(experts_bio, orient='index')

# 4.2. Merge 

df = temp1
df = df.merge(temp2, left_index = True, right_index = True)
df = df.merge(temp3, left_index = True, right_index = True)
df = df.merge(temp4, left_index = True, right_index = True)

# 4.3. Rename columns

df = df.reset_index()
df.columns = ["name", "pronoun", "role", "link", "bio"]

# 4.4. Add date accessed

df["date_request"] = date_request
df["firm"] = "Frontier Economics"


# 4.5. Save 

df.to_csv(path + "\\03 Clean data\\Frontier Economics " + date_request + ".csv", 
          index = False,
          encoding = "utf-8")