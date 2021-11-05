## 03 Import Charles Rivers Associates

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

cache = path + "\\07 Cache\\03 CRA"
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

    all_url = "https://www.crai.com/our-people/?page=60&sort=role"
    all_request = get(all_url)
    
    html_filename = cache + "\\All experts " + today + ".html"
    with open(html_filename, 'wb') as f:
            f.write(all_request.content)
            f.close()


## 2.2. Import cache version 

all_file = path + "\\07 Cache\\03 CRA\\All experts " + date_request + ".html"
all_html = codecs.open(all_file, 'r')
all_soup = BeautifulSoup(all_html, 'html.parser')


## 2.3. Get list of all experts from "All experts" page

experts_link = {}

for link in all_soup.select("a.PersonCard__name"):
    name = link.text
    name = clean_string(name)
    name = name.replace("\"", "'")
    experts_link[name] = "https://www.crai.com" + link['href']


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

experts_role = {}
experts_location = {} 
experts_bio = {} 
name_error = []

indiv_path = cache + "\\Experts " + date_request

for name, link in experts_link.items():

    # Import cache version of the expert's page 
    
    indiv_filename = indiv_path + "\\" + name + ".html"
    indiv_html = codecs.open(indiv_filename, 'r')
    indiv_soup = BeautifulSoup(indiv_html, 'html.parser')
    
    # Check whether page is correct - deal with errors later
    
    error_page = indiv_soup.select_one("div.Error__content")
    if error_page != None:
        name_error.append(name)
        continue

    # Check name is the same
    
    name_temp = indiv_soup.select_one("h1.PeopleHero__name").text
    name_temp = clean_string(name_temp)
    name_temp = name_temp.replace("\"", "'")
    assert name == name_temp
    
    # Role
    
    role = indiv_soup.select_one("div.PeopleHero__role").text
    experts_role[name] = role

    # Location
    
    loc_temp = indiv_soup.select("ul.PeopleHeroContact__locations a.PeopleHeroContact__link[href*=location]")
    location = ""
    for loc in loc_temp:
        loc = loc.text
        loc = clean_string(loc)
        location = location + " and " + loc
    location = clean_string(location)
    location = re.sub(r'^(and\s)', '', location)
    experts_location[name] = location
    
    # Biography

    bio_body = indiv_soup.select_one("div.PeopleHero__bio")
    if bio_body != None:
        bio_body = bio_body.text 
        bio_body = clean_string(bio_body)

    bio_intro = indiv_soup.select_one("div.PeopleHero__intro")
    if bio_intro != None:
        bio_intro = bio_intro.text
        bio_intro = clean_string(bio_intro)
        bio = bio_intro + " " + bio_body

    if bio_intro == None and bio_body != None:
        bio = bio_body 
        
    elif bio_intro == None and bio_body == None:
        bio = ""
                    
    bio = clean_string(bio)
    experts_bio[name] = bio

## 3.3. Manually import data for problematic names with error

# (1) Raphaël de Coninck 

name = "Raphaël De Coninck"

experts_role[name] = "Vice President"
experts_location[name] = "Brussels"

bio = """
Dr. Raphaël De Coninck heads CRA’s Brussels office. Raphaël has provided expert economic evidence and testimony in numerous high profile cases covering antitrust and competition matters (including over 60 mergers and 20 “Phase II” merger investigations, abuses of dominance and cartels), intellectual property and damages quantification.
He has advised clients in litigation and regulatory proceedings in front of the European Commission and of national courts and authorities, primarily in Belgium, France, the Netherlands, the United Kingdom, Spain, and Switzerland.
Raphaël’s experience spans a wide range of products and industries, including pharmaceuticals, IT, consumer products and retail, transport, telecoms, energy, basic industries, financial services, media and entertainment. While at CRA, he has worked for clients such as Universal Music Group, Google, Dolby, Pfizer, Novartis, Mylan, Baxter, Abbott, GE, Virgin Atlantic, Danone, Henkel, L’Oréal, ABF, Ahold Delhaize, FIFA, Cable Europe, Canal+, SFR, Deutsche Bank, JP Morgan, and the European Commission.
Prior to joining CRA, Raphaël was a member of DG Competition’s chief economist team at the European Commission. He has published numerous articles on the economics of competition and contributed to major competition policy initiatives, including the European Commission’s Best Practices for Economic Submissions and Data Collection in Merger and Antitrust Cases, and the European Commission’s Practical Guide on the Quantification of Antitrust Damages.
Raphaël received a PhD in economics from the University of Chicago, and degrees in law and in economics from the University of Liège, Belgium. He previously lectured on law and economics at the University of Chicago, held an academic position at New York University School of Law, and is currently teaching on competition policy at the Free University of Brussels (ULB) and at the Brussels School of Competition (BSC).
"""
bio = clean_string(bio)
experts_bio[name] = bio

name_error.remove(name)

# (2) Cécile Matthews

name = "Cécile Matthews"

experts_role[name] = "Vice President"
experts_location[name] = "Cambridge"

bio = """
Cécile Matthews is a vice president in the Life Sciences Practice and has 20 years of experience in strategy consulting for the life sciences industry.
Cécile Matthews leverages her expertise in pricing and market access to provide her clients with strategic insights on how to best prepare for launch and optimize revenues. Her areas of expertise include pricing, reimbursement, and market access on issues affecting biopharmaceuticals globally. She has deep experience working in oncology and rare diseases.
In oncology, Cécile has completed many assignments on i-os, targeted therapies, biosimilars, and companion diagnostics tackling issues such as early access, launch sequence, drivers of access, global pricing and access strategies, and launch readiness activities. In rare diseases, she has advised and published on issues such as early access, leveraging patient involvement, strategies to address uncertainty of evidence, and global pricing and market access strategies. She is particularly renowned for her expert knowledge of France.
Throughout her consulting career, Cécile has worked with clients on many aspects of the life science industry including biopharmaceuticals, medical devices, vaccines, and mobile health applications. Before joining CRA, Cécile was a principal at Eradigm Consulting, an insights and strategy consulting firm, and worked as an independent consultant and at Cambridge Pharma Consultancy/IMS Pricing and Reimbursement, now IQVIA.
Cécile is a dual French/British national.
"""
bio = clean_string(bio)
experts_bio[name] = bio

name_error.remove(name)

# (3) Uğur Akgün

name = "Uğur Akgün"

experts_role[name] = "Director"
experts_location[name] = "London"

bio = """
Uğur specializes in applying industrial organization theory in merger, abuse of dominance, and dispute cases. He has substantial experience in developing theoretical models which inform on effects of mergers and regulatory actions. His work for merging parties on the European Commission’s Phase II investigations includes ASL/Arianespace, UTC/Goodrich, and Posten/Post Danmark which involved conglomerate effects concerns and INEOS/SolVay and BHB/RioTinto JV in which production capacity and utilization rates were considered as important elements of competition.
A notable experience was working for Aer Lingus during the EC’s review of Ryanair’s last hostile takeover bid which led to a prohibition decision and throughout the UK investigation by which Ryanair was required to divest most of its minority shareholding in Aer Lingus. He has also assisted Sky in reversing the Competition Commission’s provisional finding of dominance during movies on pay-TV market investigation.
In addition to cases before the European Commission, the CMA, the UK Competition Appeals Tribunal, ICSID, and the WTO, Uğur has worked on cases in non-EU jurisdictions. For example, in Turkey he helped Mars and AFM, the two leading two cinema chains, gain approval of their merger. He has worked on projects in aerospace, airline, automotive parts, broadcasting transmission, film exhibition, chemical, electricity generation, energy retail, FMCG, grocery retail, mining, pay-TV, postal, telecommunication, tobacco, and truck industries.
Uğur speaks English, Spanish, and Turkish. His academic work was published in the Journal of Industrial Economics and the B.E. Journal of Economic Analysis and Policy.
"""
experts_bio[name] = bio

name_error.remove(name)

# (4) Mikaël Hervé

name = "Mikaël Hervé"

experts_role[name] = "Principal"
experts_location[name] = "London"

bio = """
Mikaël Hervé is a principal in Charles River Associates’ European Competition Practice, sharing his time between CRA’s London and Paris offices.
He is an expert in the application of econometric techniques to competition issues involving antitrust cases (cartels, abuse of dominant position, market coordination), mergers, and damages quantification.
His work has covered numerous high-profile cases advising clients in front of the European Commission, national courts and authorities in France, Belgium, the UK and Australia.
He has particularly extensive experience in the ad tech space (working for specialised search engines, global mass media corporations and a price comparison website in various jurisdictions in France, UK, US and Australia), in the assessment of local competition (either at the European or national level e.g. between supermarkets or production plants) and in the evaluation of damages.
His work covers a wide range of industries in the context of mergers (e.g. Disney/21st Century Fox, Danone/White Wave, Safran/Oberthur, Europcar/Buchbinder/Goldcar, Novelis/Aleris, Fnac/Darty, ArianeSpace/ASL, Ahold/Delhaize); abuse of dominance (e.g. work for complainants in the Google Shopping/AdSense cases and in a number of ongoing cases in the digital and pharmaceuticals sectors); market coordination and collusion (e.g. EC truck cartel, EC CDS/libor manipulation, “yogurt cartel” in France, price-fixing in body care products in France) and damages litigation (multiple follow-on cases working e.g. for Volvo/Renault Trucks, Beiersdorf, SFR).
Mikaël has received a double degree as a Statistician-Economist from ENSAE Paris and in Managerial and Financial Economics from HEC Paris Business School.
"""
bio = clean_string(bio)
experts_bio[name] = bio

name_error.remove(name)

# (5) Patricia Peláez

name = "Patricia Peláez"

experts_role[name] = "Principal"
experts_location[name] = "Chicago"

bio = """
Patricia works on high profile matters focusing on applying forensic analysis, governance, risk and compliance, as well as general business and financial expertise across various functions and industries with a focus on conducting complex investigations and assisting clients reaffirm their commitment to integrity by independently responding to allegations of fraud, abuse, misconduct, and non-compliance.
She has served as the project manager on compliance assessments engagements, led Compliance Monitoring Program projects pursuant to the regulator’s expectations, and investigated possible fraud and non-compliance related matters. She also helps lead the Forensic Services Blockchain and Cryptocurrency solution.
She has extensive experience performing readiness assessments for providers and pharmaceutical companies executing Corporate Integrity Agreements (CIA) with the Office of Inspector General (OIG) and Provider self-disclosure matters. She has also worked on large and mid-tier financial institution clients, focusing on compliance matters, including look backs and performing compliance assessments of financial investigations units’ processes and procedures.
Patricia is a member of the American Institute of Certified Public Accountants (AICPA), the Association of Certified Fraud Examiners (ACFE), and the Illinois Association of Healthcare Attorneys (IAHA). She is a Certified Public Accountant (CPA) in the state of Illinois, Certified in Financial Forensics (CFF), a Certified Fraud Examiner (CFE), a Certified Professional Coder (CPC – A), and a Certified Anti-Money Laundering Specialist (CAMS).
"""
bio = clean_string(bio)
experts_bio[name] = bio

name_error.remove(name)

# (6) Sebastian Panthöfer

name = "Sebastian Panthöfer"

experts_role[name] = "Associate Principal"
experts_location[name] = "Brussels"

bio = """
Sebastian Panthöfer is an associate principal at Charles River Associates’ European Competition Practice in Brussels.
Prior to joining CRA, Sebastian completed a PhD in Economics at the Universidad Carlos III de Madrid. Sebastian is an applied microeconomist with expertise in health economics, industrial organization, and law and economics. His research has been published in Health Economics and he has refereed for a number of academic journals.
"""
bio = clean_string(bio)
experts_bio[name] = bio

name_error.remove(name)

# Check no name left

assert name_error == []


## 3.4. Get pronouns from biography

experts_pronoun = {}

for name, bio in experts_bio.items():
     
    # Get pronouns
    
    bio = bio.lower()

    she = bool(re.search("\sshe\s", bio)) or bool(re.search("\sher\s", bio)) or bool(re.search("\smrs\.", bio))
    he = bool(re.search("\she\s", bio)) or bool(re.search("\shis\s", bio)) or bool(re.search("\smr\.", bio))
    
    they = False
    if she == False and he == False: 
        they = bool(re.search("\sthey\s", bio))

    # Manual changes
    
    if name == "Anthony Barbera":
        he = True # based on picture
    
    if name == "Robert J. Larner":
        he = True # based on Google search
    
    if name == "Gary L. Roberts":
        he = True # based on picture
                
    if name == "Michael Swiatkowski":
        he = True # based on picture
    
    if name == "Jennifer D'Arcangelo":
        she = True # based on LinkedIn picture
        
    if name == "Artes Haderi":
        she = True # based on picture
    
    if name == "Kristopher Hult":
        he = True # based on LinkedIn picture
    
    if name == "James P. Lee":
        he = True # based on picture
        
    if name == "Margarita Patria":
        she = True # based on picture
        
    if name == "Veska Suleva":
        she = True # based on picture
    
    if name == "Rosa Tye":
        she = True # based on picture
    
    if name == "Michael Agne":
        he = True # pic
    
    if name == "Jake Arakal":
        he = True # pic
    
    if name == "Kyle Bernhard":
        he = True # based on name (no pic)

    if name == "Brooke Bonet":
        she = True # pic
    
    if name == "Desislava Byanova":
        she = True # pic
    
    if name == "Shrinidhi Chakravarthy":
        he = True # pic
        
    if name == "Daniel DeSantis":
        he = True # pic
    
    if name == "Powell Dixon":
        he = True # name (no pic)
    
    if name == "Imrran Halari":
        he = True # pic
    
    if name == "Naveen Kohli":
        he = True # LinkedIn pic 
    
    if name == "Hui Li":
        she = True # LinkedIn pic
    
    if name == "Lian Liu":
        he = True # pic
    
    if name == "Jerry Lo":
        he = True # LinkedIn pic
    
    if name == "Jania Mackenthun":
        she = True # LinkedIn pic
    
    if name == "Billy Muttiah":
        he = True # pic
    
    if name == "Greta Olesen":
        she = True # pic
    
    if name == "Michele Pistollato":
        he = True # pic
    
    if name == "Lalitha Ramkumar":
        she = True # pic
    
    if name == "Sonia Reif":
        she = True # pic

    if name == "Lauren Richardson":
        she = True # pic     
        
    if name == "Benjamin Roin":
        he = True # LinkedIn pic

    if name == "Travis Ruch":
        he = True # LinkedIn pic  
        
    if name == "Diana Saenz":
        she = True # pic

    if name == "Alexandra Whitford":
        she = True # pic    
        
    # Check pronouns 
    
    assert she != he
    assert they == False # no "they" pronouns
    
    if she == True:
        experts_pronoun[name] = "she"
    
    elif he == True:
        experts_pronoun[name] = "he"
    
    elif they == True:
        experts_pronoun[name] = "they" # In theory not needed because no "they" pronouns


##---------------------------------------------------
## 4. Export data set
##---------------------------------------------------

## 4.1. Create multiple dataframes for merge

temp1 = pd.DataFrame.from_dict(experts_pronoun, orient='index')
temp2 = pd.DataFrame.from_dict(experts_role, orient='index')
temp3 = pd.DataFrame.from_dict(experts_location, orient='index')
temp4 = pd.DataFrame.from_dict(experts_link, orient='index')
temp5 = pd.DataFrame.from_dict(experts_bio, orient='index')

## 4.2. Merge 

df = temp1
df = df.merge(temp2, left_index = True, right_index = True)
df = df.merge(temp3, left_index = True, right_index = True)
df = df.merge(temp4, left_index = True, right_index = True)
df = df.merge(temp5, left_index = True, right_index = True)

## 4.3. Rename columns

df = df.reset_index()
df.columns = ["name", "pronoun", "role", "location", "link", "bio"]

## 4.4. Add date accessed

df["date_request"] = date_request
df["firm"] = "CRA"

## 4.5. Save 

df.to_csv(path + "\\03 Clean data\\CRA " + date_request + ".csv", 
          index = False,
          encoding = "utf-8")