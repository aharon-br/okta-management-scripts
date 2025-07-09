import os
from libs.functions import okta_api_call, get_okta_token_read_only
import argparse
import csv
import urllib.parse

'''
helps search okta logs into a csv
inputs the search with -f
wrap the input strings in single quotes
'''


def build_query():
    # use argparse to get the arguments supplied at run time
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filter",
                        help="the search filter, wrap in single quotes")
    parser.add_argument("-l", "--limit",
                        help="the limit of results e.g. 10", type=int,
                        default=25)
    parser.add_argument("-o", "--order",
                        help="sort order, DESCENDING or ASCENDING, wrap in single quotes",
                        default="DESCENDING")
    args = parser.parse_args()
    # encode the filter into url encoding
    url_encoded_filter = urllib.parse.quote(args.filter, safe='')
    # construct the full search URL
    # search_url = f"{base_url}?filter={url_encoded_filter}&limit={args.limit}&sortOrder={args.order}"
    query = {
    	"filter": args.filter,
    	"limit": args.limit,
    	"sortOrder": args.order
    }
    return query


def log_parser(data):
    # create an empty array for each line
    lines = []
    # add the headers to the arrray
    headers = ["actor", "eventType", "result", "reason", "registered", "managed", "policy rule", "date"]
    lines.append(headers)
    for item in data:
        '''
        change the stuff its outputting here
        this is build for outputting around user logins
        and management status
        '''
        actor = f'{item["actor"]["alternateId"]}'
        # if the device object exists, output the status of managed and registered
        if item["device"]:
            device_registered = f"{item["device"]["registered"]}"
            device_managed = f"{item["device"]["managed"]}"
        else:
            device_registered = ""
            device_managed = ""
        date = f'{item["published"]}'
        event = f"{item["eventType"]}"
        result = f"{item["outcome"]["result"]}"
        reason = f"{item["outcome"]["reason"]}"
        target_display_name = ""
        # get the target name where the target type is "Rule"
        for target_item in item["target"]:
            if target_item["type"] == "Rule":
                target_display_name = f"{target_item["displayName"]}"
                break
        # add all the values to the lines array
        lines.append([actor, event, result, reason, device_registered, device_managed, target_display_name, date])
    return lines


if __name__ == "__main__":
	domain = 'example'
	scopes = "okta.logs.read"
	bearer_token = get_okta_token_read_only(scopes)
	token = f"Bearer {bearer_token}"
	url = f"https://{domain}.okta.com/api/v1/logs"
	query = build_query()
	method = 'get'
	data = None
	# use the okta_api_call function in libs to do the search
	call_output = okta_api_call(url, token, method, data, query)
	# parse the the results of the search
	lines = log_parser(call_output)
	# write it out to a csv called search results
	with open(os.path.expanduser("~/Downloads/search_results.csv"), 'w', newline='') as file:
		writer = csv.writer(file)
		writer.writerows(lines)
	print("Export complete, file in Downloads")
