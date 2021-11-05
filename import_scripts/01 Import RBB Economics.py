## 01 Import RBB Economics

##---------------------------------------------------
## Table of contents
## 1. Set up 
## 2. Extract list of all experts
## 3. Extract information from individual expert page
## 4. Extract CVs
## 5. Export data set
##---------------------------------------------------

##---------------------------------------------------
## 1. Set up 
##---------------------------------------------------

## 1.1. Import libraries

import os
import re
import string
import codecs
import PyPDF2
import pandas as pd 

from requests import get
from bs4 import BeautifulSoup


## 1.2. Set up path 

path = "D:\\OneDrive\\CODE\\PROJECTS\\Data-Scraping-Gender-in-economic-consulting-firms"
os.chdir(path)

cache = path + "\\07 Cache\\01 RBB Economics"
if not os.path.exists(cache):
    os.makedirs(cache)

    
## 1.3. Import programs and today's date

programs = path + "\\02 Scripts\\01 Import\\00 Import programs.py"
exec(open(programs).read())


## 1.4. Prepare variables which affect requests/cache

make_requests = False # If True: makes the requests on the internet

if make_requests == True:
    date_request = today
else:
    date_request = "03-02-2021"


##---------------------------------------------------
## 2. Extract list of all experts
##---------------------------------------------------

## 2.1. Import html file and save

if make_requests:

    all_url = "https://www.rbbecon.com/our-experts/"
    all_request = get(all_url)
    
    html_filename = cache + "\\All experts " + today + ".html"
    with open(html_filename, 'wb') as f:
            f.write(all_request.content)
            f.close()


## 2.2. Import cache version 

all_file = cache + "\\All experts " + date_request + ".html"
all_html = codecs.open(all_file, 'r')
all_soup = BeautifulSoup(all_html, 'html.parser')


## 2.3. Get list of all experts from "All experts" page

experts_link = {}

for link in all_soup.select("div.experts a"):
    experts_link[link.text] = link['href']


##---------------------------------------------------
## 3. Extract information from individual expert page
##---------------------------------------------------

## 3.1. Get the expert pages and save 

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


## 3.2. Import cache version and extract information

experts_location = {} # Taken from header
experts_bio = {} # Biography (text)
experts_cv = {} # Link to CV

indiv_path = cache + "\\Experts " + date_request

for name, link in experts_link.items():
    
    # Import cache version of the expert's page 
    indiv_filename = indiv_path + "\\" + name + ".html"
    indiv_html = codecs.open(indiv_filename, 'r')
    indiv_soup = BeautifulSoup(indiv_html, 'html.parser')
    
    # Check name is the same
    name_temp = indiv_soup.select_one("div.profile_header p.name").text
    name_temp = clean_string(name_temp)
    assert name == name_temp
    
    # Location
    location = indiv_soup.find("div", class_ = "profile_header").find("p", class_ = None).text
    experts_location[name] = location
    
    # Biography
    bio = indiv_soup.select_one("div.profile_bio").text
    bio = clean_string(bio)
    experts_bio[name] = bio
    
    # CV link 
    experts_cv[name] = "https://www.rbbecon.com" + indiv_soup.select_one("div.profile_bio a")["href"]


## 3.3. Get pronouns from biography

experts_pronoun = {}

for name, bio in experts_bio.items():
 
    bio = bio.lower()

    she = bool(re.search("\sshe\s", bio))
    he = bool(re.search("\she\s", bio))
    they = bool(re.search("\sthey\s", bio))

    assert she != he
    assert they == False # no "they" pronouns
    
    if she == True:
        experts_pronoun[name] = "she"
    
    elif he == True:
        experts_pronoun[name] = "he"
    
    elif they == True:
        experts_pronoun[name] = "they" # In theory not needed because no "they" pronouns


##---------------------------------------------------
## 4. Extract CVs
##---------------------------------------------------

## 4.1. Download CVs

if make_requests:
    
    cv_dir_today = cache + "\\CV " + today
    if not os.path.exists(cv_dir_today):
        os.makedirs(cv_dir_today)
    
    for name, link in experts_cv.items():
        
        response = get(link)
        cv_filename = cv_dir_today + "\\" + name + ".pdf"
        
        with open(cv_filename, 'wb') as f:
            f.write(response.content)
            f.close()
        
## 4.2. Import cache of CVs and transform into text files
# This section is taken from: https://medium.com/better-programming/how-to-convert-pdfs-into-searchable-key-words-with-python-85aab86c544f

cv_dir = cache + "\\CV " + date_request
    
for name, link in experts_cv.items():
    
    cv_filename = cv_dir + "\\" + name + ".pdf"
    cv_textfile = cv_dir + "\\" + name+ ".txt"
    
    pdf_file_obj = open(cv_filename, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    
    num_pages = pdf_reader.numPages
    count = 0
    text = ""
    
    while count < num_pages:
        page_obj = pdf_reader.getPage(count)
        count += 1
        text += page_obj.extractText()
    
    with open(cv_textfile, 'w') as f:
        f.write(text)
        f.close()

## 4.3. Get roles from CVs

experts_role = {}

for name, link in experts_cv.items():
  
    cv_textfile = cv_dir + "\\" + name + ".txt"
    text = open(cv_textfile, 'r')
    text = text.read()

    # Deal with non-standard characters which were not processed correctly
    
    name_temp = name
    
    if name == "Benoît Durand":
        name_temp = "Benoﬂt Durand"
        
    if name == "Enrique Cañizares":
        name_temp = "Enrique CaŒizares"
    
    if name == "Joan de Solà-Morales":
        name_temp = "Joan de Sol‹ -Morales"
        
    if name == "Jimmy Gårdebrink":
        name_temp = "Jimmy G „rdebrink"
    
    if name == "Clément Delhon":
        name_temp = "Cl”ment Delhon"
    
    if name == "Kryštof Krotil":
        name_temp = "Kry ! tof Krotil"
        
    if name == "J. Roberto Parra-Segura":
        name_temp = "J. Roberto Parra Segura"

    if name == "Christoffer Theilgaard":
        name_temp = "Christoffer Haag Theilgaard"
        
    # Find role in text
    
    text = text.replace("\n", " ")
    text = text.replace("  ", " ")
    
    pattern = re.compile(name_temp + "([a-zA-Z\s]*)")
    matches = re.findall(pattern, text)    
       
    role = matches[0]
    role = role.translate(str.maketrans('', '', string.punctuation)) # Remove punctuation
    role = role.strip() # String spaces
    role = role.lower()
    
    # Clean role
    
    if role == "is a partner based in rbb":
        role = "partner"
    
    if role == "associat e principal":
        role = "associate principal"
    
    experts_role[name] = role


##---------------------------------------------------
## 5. Export data set
##---------------------------------------------------

## 5.1. Create multiple dataframes for merge

temp1 = pd.DataFrame.from_dict(experts_pronoun, orient='index')
temp2 = pd.DataFrame.from_dict(experts_role, orient='index')
temp3 = pd.DataFrame.from_dict(experts_location, orient='index')
temp4 = pd.DataFrame.from_dict(experts_link, orient='index')
temp5 = pd.DataFrame.from_dict(experts_cv, orient='index')
temp6 = pd.DataFrame.from_dict(experts_bio, orient='index')

## 5.2. Merge 

df = temp1
df = df.merge(temp2, left_index = True, right_index = True)
df = df.merge(temp3, left_index = True, right_index = True)
df = df.merge(temp4, left_index = True, right_index = True)
df = df.merge(temp5, left_index = True, right_index = True)
df = df.merge(temp6, left_index = True, right_index = True)

## 5.3. Rename columns

df = df.reset_index()
df.columns = ["name", "pronoun", "role", "location", "link", "cv_link", "bio"]

## 5.4. Add date accessed

df["date_request"] = date_request
df["firm"] = "RBB Economics"

## 5.5. Save 

df.to_csv(path + "\\03 Clean data\\RBB Economics " + date_request + ".csv", 
          index = False,
          encoding = "utf-8")