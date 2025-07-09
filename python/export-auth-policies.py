import json
import os
from pathlib import Path
from libs.functions import okta_api_call, get_okta_token_read_only



scopes = "okta.policies.read"
# get a token
token = get_okta_token_read_only(scopes)
bearer_token = f"Bearer {token}"

domain = "example"
base_url = f"https://{domain}.okta.com/api/v1"
method = 'get'

dest_folder = Path.home() / "Downloads" / "auth_policies"
dest_folder.mkdir(parents=True, exist_ok=True)  # create the folder if needed, handle it already existing with no error



def get_policies():
    policy_url = f"{base_url}/policies"
    query = {
    "type": "ACCESS_POLICY"
    }
    policies = okta_api_call(policy_url, bearer_token, method, None, query)
    return policies



def get_rules(policies):
    for policy in policies:
        # get the policy name and ID
        policy_id = policy["id"]
        policy_name = policy["name"]
        
        # creat the folder for the policy itself using the policy name
        folder_name = dest_folder / policy_name
        folder_name.mkdir(exist_ok=True)  # if it exists already just make it
            
        policy_rule_url = f"{base_url}/policies/{policy_id}/rules"
        policy_rules = okta_api_call(policy_rule_url, bearer_token, method)
    
        for rule in policy_rules:
            rule_id = rule["id"]
            
            rule_url = f"{policy_rule_url}/{rule_id}"
            rule_object = okta_api_call(rule_url, bearer_token, method)
    
            rule_name = rule_object.get("name").replace("/", ":")  # get the rule name, replace / to :
            priority = rule_object.get("priority")  # get the rule priority
            filename = f"{priority}-{rule_name}.json"  # creat the file name as priority number-name e.g "0-Deny"
    
            rule_path = folder_name / filename  # path to write out to is the current folder for the policy plus the file
            with open(rule_path, "w") as f:
                json.dump(rule_object, f, indent=2)
                

if __name__ == "__main__":
    policies = get_policies()
    rules = get_rules(policies)
    
    message = """Export complete,
    check your downloads"""
    print(message)