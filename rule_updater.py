import csv
import requests
import os
import json

"""
takes the rules listed in a CSV, and for any that are status active will update them with the conditions in the CSV
it will still do it if they are the same, it causes no harm most of the time
"""

# get the token from the environment variable of okta_token, or ask for it
if os.environ.get('okta_token'):
    token = os.environ.get('okta_token')
else:
    token = getpass('no token in env file, paste api token here:\n')

# set the okta domain
domain = ""
    
# set the headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"SSWS {token}"
}

# read the rules from the csv called "rules.csv" in the same directory, update as needed
with open("rules.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    # read each row
    for row in reader:
        # if the rule is active
        if row["rule_status"] == "ACTIVE":
            rule_id = row["rule_id"]
            rule_name = row["rule_name"]
            new_rule_conditions = row["rule_conditions"] # read the conditions from the conditions column

            # deactivate the rule so we can update it
            url = f"https://{domain}.okta.com/api/v1/groups/rules/{rule_id}/lifecycle/deactivate"
            response = requests.post(url, headers=headers)
            response.raise_for_status() # raise error if not 200
            
            # get the rule to have the full body so we can update it
            url = f"https://{domain}.okta.com/api/v1/groups/rules/{rule_id}"
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # raise error if not a 200 status
            rule_body = response.json()

            # put and update the rule
            url = f"https://{domain}.okta.com/api/v1/groups/rules/{rule_id}"

            # update ONLY the conditions object
            rule_body["conditions"]["expression"]["value"] = new_rule_conditions

            response = requests.put(url, headers=headers, json=rule_body)
            response.raise_for_status() # raise error if not 200

            # reactivete the rule
            url = f"https://{domain}.okta.com/api/v1/groups/rules/{rule_id}/lifecycle/activate"

            response = requests.post(url, headers=headers)
            response.raise_for_status() # raise error if not 200

            # output on screen when its done
            print(f"Rule {rule_name} updated and reactivated successfully.")

# output on screen when all are done
print("Finished processing rules.")