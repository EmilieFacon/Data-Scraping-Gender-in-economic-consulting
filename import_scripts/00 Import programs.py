## 00 Import programs

# Import libraries

import datetime

# Clean strings

def clean_string(my_string):
    my_string = my_string.replace("\n", " ") # New line
    my_string = my_string.replace("\xa0", " ") # Non-breaking space
    my_string = my_string.replace("    ", " ") # Four spaces
    my_string = my_string.replace("   ", " ") # Three spaces    
    my_string = my_string.replace("  ", " ") # Double spaces
    my_string = my_string.strip() # Leading and trailing spaces
    return(my_string)
    
# Today's date 
    
now = datetime.datetime.now()
today = now.strftime("%d") + "-" + now.strftime("%m") + "-" + now.strftime("%Y") # DMY format