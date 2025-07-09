import requests
import json
import os
import csv

"""
this searches okta rules for the search terms provided and outputs a list of those rules for auditing
"""

# get the token from the environment variable of okta_token, or ask for it
if os.environ.get('okta_token'):
    token = os.environ.get('okta_token')
else:
    token = getpass('no token in env file, paste api token here:\n')

# set the okta domain
domain = ""

# create the csv and header names
with open(os.path.expanduser("~/Downloads/rules.csv"), "w") as f:
    f.write("rule_id,rule_status,rule_name,rule_conditions,assigned_group_ids,assigned_group_names\n")

"""
this is set to be a file called "search_terms.csv" in the same directory as this script, adjust if you need it to be something else
the search terms can be anything you are looking for, it might be a list of cost centers, e.g.
    Sales
    HR
    or it might manager emails to see if they are in rules, e.g.
    jdoe@domain.com
    eodj@domain.com
"""
with open("search_terms.csv", "r") as f: # get the search terms from the csv of search terms
    for search_term in f:
        search_term = search_term.strip().replace(" ", "%20") # replace the spaces in the search terms with url encoding

        # get the rules that match the search term
        url = f"https://{domain}.okta.com/api/v1/groups/rules?search={search_term}&expand=groupIdToGroupNameMap"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SSWS {token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # raise error if not a 200 status
        rules = response.json()
        
        # for any rules found from the search, iterate over and get the details
        for rule in rules:

            # get the details from the object
            rule_id = rule["id"]
            rule_status = rule["status"]
            rule_name = rule["name"]
            rule_conditions = rule["conditions"]["expression"]["value"]
            assigned_group_ids_print = ", ".join(rule["actions"]["assignUserToGroups"]["groupIds"]) # make this one look nice
            assigned_group_ids = rule["actions"]["assignUserToGroups"]["groupIds"] # this stays an array so we can use in the group name
            # this is more annoying, we need get the list of group IDs in the ID to name list, find the ones in the assignment group Id list and print those
            # the group ID to name object contains all the groups featured in the rule, including any from the condition itself
            assigned_group_names = ", ".join(
                rule["_embedded"]["groupIdToGroupNameMap"][group_id]
                for group_id in assigned_group_ids
                if group_id in rule["_embedded"]["groupIdToGroupNameMap"]
                and rule["_embedded"]["groupIdToGroupNameMap"][group_id] is not None
            )

            # write out to a csv
            with open(os.path.expanduser("~/Downloads/rules.csv"), "a", newline="") as csv_file:
                writer = csv.writer(csv_file) # we need to use csv writer here as the rule conditions can contain linebreaks that we need to handle without them causing multiple lines
                writer.writerow([rule_id, rule_status, rule_name, rule_conditions, assigned_group_ids_print, assigned_group_names])

print("Export in downloads")