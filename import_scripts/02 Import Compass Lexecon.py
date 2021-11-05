## 02 Import Compass Lexecon

##---------------------------------------------------
## Table of contents
##---------------------------------------------------

##---------------------------------------------------
## 1. Set up 
##---------------------------------------------------

## 1.1. Import libraries

import os
import re
import string
import codecs
import pandas as pd 

from bs4 import BeautifulSoup
from requests import get


## 1.2. Set up path 

path = "D:\\OneDrive\\CODE\\PROJECTS\\Data-Scraping-Gender-in-economic-consulting-firms"
os.chdir(path)

cache = path + "\\07 Cache\\02 Compass Lexecon"
if not os.path.exists(cache):
    os.makedirs(cache)

    
## 1.3. Import programs and today's date

programs = path + "\\02 Scripts\\01 Import\\00 Import programs.py"
exec(open(programs).read())


## 1.4. Prepare variables which affect requests/cache

date_all_experts = "03-02-2021"
make_requests = False # If True: makes the requests on the internet

if make_requests == True:
    date_request = today
else:
    date_request = "03-02-2021"


##---------------------------------------------------
## 2. Extract list of all experts
##---------------------------------------------------

## 2.1. Import cache version of html 

all_file = path + "\\01 Input data\\02 Compass Lexecon\\All experts " + date_all_experts + ".html"
all_html = codecs.open(all_file, 'r')
all_soup = BeautifulSoup(all_html, 'html.parser')


## 2.2. Get list of all experts

experts_link = {}
experts_role = {}

wrappers = all_soup.select(".filter__professional-row-wrapper")

for wrapper in wrappers:
        
    name = wrapper.select_one("a.filter__professional-name-link").text
    name = clean_string(name)

    link = wrapper.select_one("a.filter__professional-name-link")["href"]
    experts_link[name] = link
    
    role = wrapper.select_one("p.filter__professional-title").text
    experts_role[name] = role


##---------------------------------------------------
## 3. Extract information from individual expert page
##---------------------------------------------------

## 3.1. Get the expert page and save 

if make_requests:

    cache_expert = cache + "\\Experts " + today
    if not os.path.exists(cache_expert):
        os.makedirs(cache_expert)
        
    for name, link in experts_link.items():
    
        # Need headers to make the request - see https://stackoverflow.com/questions/38489386/python-requests-403-forbidden
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        # Get the expert's page
        indiv_request = get(link, headers = headers)
        indiv_filename = cache_expert + "\\" + name + ".html"
        with open(indiv_filename, 'wb') as f:
            f.write(indiv_request.content)
            f.close()


## 3.2. Import cache version and extract information

experts_location = {} 
experts_bio = {} 
experts_uni = {} 

indiv_path = cache + "\\Experts " + date_request

for name, link in experts_link.items():
        
    # Import cache version of the expert's page 
    indiv_filename = indiv_path + "\\" + name + ".html"
    indiv_html = codecs.open(indiv_filename, 'r')
    indiv_soup = BeautifulSoup(indiv_html, 'html.parser')
    
    # Name (to check it is consistent with name on all experts page)
    name_temp = indiv_soup.select_one("div.professional__full-name-wrapper").text
    name_temp = clean_string(name_temp)
    assert name_temp == name
    
    # Title (to check it is consistent with title on all experts page)
    role_temp = indiv_soup.select_one("div.professional__position-wrapper").text
    assert role_temp == experts_role[name]
    
    # Location
    location = indiv_soup.select_one("div.professional__locations-wrapper")
    if location != None:
        location = location.text 
        location = clean_string(location)
        experts_location[name] = location 
    if location == None:
        experts_location[name] = "N/A"

    # Bio 
    bio = indiv_soup.select_one("div.professional__description").text
    bio = clean_string(bio)
    experts_bio[name] = bio
    
    # Uni (not clean)
    uni = indiv_soup.select_one("div.professional__degree")
    experts_uni[name] = uni 


## 3.3. Get pronouns from biography

experts_pronoun = {}

for name, bio in experts_bio.items():
 
    bio = bio.lower()

    she = bool(re.search("\sshe\s", bio))
    he = bool(re.search("\she\s", bio))
    they = bool(re.search("\sthey\s", bio))

    if she == False and he == False:
        she = bool(re.search("\sher\s", bio))
        he = bool(re.search("\shis\s", bio))
        
    # Manual checks to biographies which do not pass the asserts
    
    if name == "Alessandro Bonatti":
        they = False # "how they collect, mine, and monetize information"
    
    if name == "Aynat Geffen":
        she = True # based on picture
    
    if name == "Alyssa W. Lam":
        she = True # based on picture
    
    if name == "Stephen D. Makowka":
        they = False # "how they react when that environment is affected by policy changes"
        
    if name == "Hila Nevo":
        she = True # based on picture
    
    # Check only one pronoun 

    assert she != he
    assert they == False # No one uses "they"
    
    if she == True:
        experts_pronoun[name] = "she"
    
    elif he == True:
        experts_pronoun[name] = "he"
    
    elif they == True:
        experts_pronoun[name] = "they" # No one uses "they" so this is technically not necessary


##---------------------------------------------------
## 4. Export data set
##---------------------------------------------------

## 4.1. Create multiple dataframes for merge

temp1 = pd.DataFrame.from_dict(experts_pronoun, orient='index')
temp2 = pd.DataFrame.from_dict(experts_role, orient='index')
temp3 = pd.DataFrame.from_dict(experts_location, orient='index')
temp4 = pd.DataFrame.from_dict(experts_link, orient='index')
temp5 = pd.DataFrame.from_dict(experts_uni, orient='index')
temp6 = pd.DataFrame.from_dict(experts_bio, orient='index')

## 4.2. Merge 

df = temp1
df = df.merge(temp2, left_index = True, right_index = True)
df = df.merge(temp3, left_index = True, right_index = True)
df = df.merge(temp4, left_index = True, right_index = True)
df = df.merge(temp5, left_index = True, right_index = True)
df = df.merge(temp6, left_index = True, right_index = True)

## 4.3. Rename columns

df = df.reset_index()
df.columns = ["name", "pronoun", "role", "location", "link", "uni", "bio"]

## 4.4. Add date accessed

df["date_request"] = date_request
df["firm"] = "Compass Lexecon"


## 4.5. Save 

df.to_csv(path + "\\03 Clean data\\Compass Lexecon " + date_request + ".csv", 
          index = False,
          encoding = "utf-8")
