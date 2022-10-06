# Jamf-Adv-Search-Email-Report
Jamf has limited functionaility for reporting based on advanced searches. This feature also just doesn't work at all on windows tomcat nodes. This script will take a passed in advanced search name, collect a list of hosts and email them to a provided email list in order to setup simple reporting.

This script by default utilizes AWS Secret manager to pull credentials but they can be manually passed in via optional setting.

The script will return the following fields sent in the email report:
Computer_Name, Last_Check_in, Username
Add more fields if needed but make sure they are also displayed on your advance search or they cannot be pulled via the API.


Setting up Dependencies
-------------------------

1. Ensure ``pip`` and ``pipenv`` are installed.
2. Clone repositiory: ``git clone git@github.com:evan684/Jamf-Adv-Search-Email-Report.git``
2. ``cd`` into the repository.
4. Fetch development dependencies ``make install``
5. Activate virtualenv: ``pipenv shell``

Usage
-----

Edit the script and set your jamf URL in the jamfURL var.

Run set the script as executable:

    $ chmod u+x jamf_adv_search_email.py
  
Run the script:
 
    $ ./jamf_adv_search_email.py
  
The script will prompt you for your jamf username and password to access the API. 

Use the --help menu for parameter more info aboout usage and optional parameters.
