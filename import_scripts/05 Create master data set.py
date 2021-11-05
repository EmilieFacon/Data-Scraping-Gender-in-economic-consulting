## 05 Create master data set

##---------------------------------------------------
## Table of contents
## 1. Set up
## 2. Import and clean data frames
## 3. Append
##---------------------------------------------------

##---------------------------------------------------
## 1. Set up 
##---------------------------------------------------

## 1.1. Import libraries

import os
import re
import string
import pandas as pd 
import numpy as np


## 1.2. Set up path 

path = "D:\\OneDrive\\CODE\\PROJECTS\\Data-Scraping-Gender-in-economic-consulting-firms"
os.chdir(path)

clean = path + "\\03 Clean data\\"


##---------------------------------------------------
## 2. Import and clean data frames
##---------------------------------------------------

## 2.1. RBB Economics

# Import

rbb = pd.read_csv(clean + "RBB Economics 03-02-2021.csv")

# Check roles and gender

rbb.groupby("role").count()["name"] # 4 roles: associate principal, partner, principal, senior associate
rbb.groupby("pronoun").count()["name"] # 54 men, 16 women

# Standardised role

rbb["role_std"] = ""
rbb.role_std[rbb.role == "partner"] = "2. Senior Management"
rbb.role_std[rbb.role == "principal"] = "3. Management"
rbb.role_std[rbb.role == "associate principal"] = "3. Management"
rbb.role_std[rbb.role == "senior associate"] = "4. Economist"
assert all(rbb.role_std != "")

# Clean location 

rbb = rbb.rename(columns={'location': 'location_raw'}) # Rename location to location_raw
rbb.groupby("location_raw").count()["name"] # Tab location 
rbb[['first_loc','second_loc']] = rbb['location_raw'].str.split(' and ', expand = True) # Split location
rbb["many_locs"] = rbb["second_loc"].notnull() # Create column which is true if 2 locations
rbb[rbb["many_locs"]] # Only London and Paris as second location


## 2.2. Compass Lexecon

# Import

compass = pd.read_csv(clean + "Compass Lexecon 03-02-2021.csv")
compass = compass[compass["name"] != "Christopher L. Culp (In Memoriam)"] # Passed away

# Clean roles

compass = compass.rename(columns = {"role": "role_raw"})
compass[["role", "second_role"]] = compass["role_raw"].str.split(" and ", expand = True) # Split people with two roles

compass.groupby("role").count()["name"]

## Promotion order: 
# Analyst
# Senior Analyst
# Economist
# Senior Economist
# Vice President
# Senior Vice President
# Executive Vice President ~ Senior Consultant
# Senior Managing Director

## Sources:
# https://www.linkedin.com/in/catherine-barron-4325596/ 
# https://www.linkedin.com/in/enrique-andreu-39304214/
# https://www.linkedin.com/in/manuel-a-abdala-46b76316/
# https://www.linkedin.com/in/bernardo-sarmento-3377a497/
# https://www.linkedin.com/in/dan-o-brien-1469a814/

# Standardised role

compass['role_std'] = "Other"
compass.role_std[compass.role == "Academic Affiliate"] = "Affiliate"
compass.role_std[compass.role == "Economist"] = "3. Management"
compass.role_std[compass.role == "Executive Vice President"] = "2. Senior Management"
compass.role_std[compass.role == "Senior Consultant"] = "2. Senior Management"
compass.role_std[compass.role == "Senior Economist"] = "4. Economist"
compass.role_std[compass.role == "Senior Managing Director"] = "1. Top Management"
compass.role_std[compass.role == "Senior Vice President"] = "3. Management"
compass.role_std[compass.role == "Vice President"] = "3. Management"

assert all(compass.role_std != "")


# Location

compass = compass.rename(columns = {'location': 'location_raw'})
compass[['first_loc','second_loc', 'third_loc']] = compass['location_raw'].str.split('  ', expand = True) # Split location
compass['many_locs'] = compass['second_loc'].notnull()


## 2.3. CRA 

# Import

cra = pd.read_csv(clean + "CRA 03-02-2021.csv")

# Clean roles

cra = cra.rename(columns = {"role": "role_raw"})
cra[["role_temp1", "role_and"]] = cra["role_raw"].str.split(" and ", expand = True) # Split people with two roles
cra[["role_temp2", "role_comma1", "role_comma2"]] = cra["role_temp1"].str.split(", ", expand = True) # Split people with two roles
cra[["role_temp3", "role_sign"]] = cra["role_temp2"].str.split(" & ", expand = True) 
cra = cra.rename(columns = {"role_temp3": "role"})

cra.groupby("role").count()["name"]

# Role hierarchy
# Consulting Associate
# Senior Associate
# Associate Principal
# Principal - https://www.linkedin.com/in/muath-masri-476aaa87/
# Vice President / Senior Consultant

# Standardised role

cra['role_std'] = "Other"
cra.role_std[cra.role == "Consulting Associate"] = "5. Analyst"
cra.role_std[cra.role == "Associate Principal"] = "4. Economist"
cra.role_std[cra.role == "Director"] = "1. Top Management"
cra.role_std[cra.role == "Principal"] = "3. Management"
cra.role_std[cra.role == "Senior Consultant to CRA"] = "2. Senior Management"
cra.role_std[cra.role == "Vice President"] = "2. Senior Management"
assert all(cra.role_std != "")

# Location

cra = cra.rename(columns = {'location': 'location_raw'})
cra[['first_loc','second_loc']] = cra['location_raw'].str.split(' and ', expand = True) # Split location
cra['many_locs'] = compass['second_loc'].notnull()


## 2.4. Frontier Economics

# Import
frontier = pd.read_csv(clean + "Frontier Economics 04-11-2021.csv")

# Check roles and gender
frontier.groupby("role").count()["name"] # roles: Analyst, Associate, Associate Director, Chairman, Consulant, Director, Manager, Senior Associate
frontier.groupby("pronoun").count()["name"] # 140 men, 85 women, 1 non-binary

# Hierarchy:
# Analyst
# Consultant
# Manager
# Associate Director
# Director

# Role standardised
frontier['role_std'] = ""
frontier.role_std[frontier.role == "Analyst"] = "5. Analyst"
frontier.role_std[frontier.role == "Associate"] = "Other"
frontier.role_std[frontier.role == "Associate Director"] = "2. Senior Management"
frontier.role_std[frontier.role == "Chairman"] = "1. Top Management"
frontier.role_std[frontier.role == "Consultant"] = "4. Economist"
frontier.role_std[frontier.role == "Director"] = "1. Top Management"
frontier.role_std[frontier.role == "Manager"] = "3. Management"
frontier.role_std[frontier.role == "Senior Associate"] = "Other"
assert all(frontier.role_std != "")


##---------------------------------------------------
## 3. Append and save
##---------------------------------------------------

df = pd.concat([rbb, cra, compass, frontier])

df.to_csv(path + "\\03 Clean data\\Full dataset " + today + ".csv", 
          index = False,
          encoding = "utf-8")