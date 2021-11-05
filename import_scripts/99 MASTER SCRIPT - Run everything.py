## 99 MASTER SCRIPT - Run everything

##---------------------------------------------------
## 1. Set up 
##---------------------------------------------------

import os
path = "D:\\OneDrive\\CODE\\PROJECTS\\Data-Scraping-Gender-in-economic-consulting-firms"
os.chdir(path)

import_scripts_path = path + "\\02 Scripts\\01 Import"

##---------------------------------------------------
## 2. Run scripts
##---------------------------------------------------

exec(open(import_scripts_path + "\\00 Import programs.py").read())
exec(open(import_scripts_path + "\\01 Import RBB Economics.py").read())
exec(open(import_scripts_path + "\\02 Import Compass Lexecon.py").read())
exec(open(import_scripts_path + "\\03 Import CRA.py").read())
exec(open(import_scripts_path + "\\04 Import Frontier Economics.py").read())
exec(open(import_scripts_path + "\\05 Create master data set.py").read())

##---------------------------------------------------
## 3. End of script
##---------------------------------------------------

print("All import scripts done.")
print("End of master script.")