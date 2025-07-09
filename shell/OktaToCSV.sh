#!/bin/zsh

############################################
## HELP ##
Help()
{
	# Display Help
	echo "Takes the relative URL for Okta API and export results to a CSV in Downloads"
	echo "Helps fill the gaps with Rockstar"
	echo
	echo "Syntax: OktaToCSV /relative/url/for/api"
	echo "Example: OktaToCSV /api/v1/users"
	echo
	echo "Large exports may take a few minutes"
	echo "Try using cskvit (csvcut or csvgrep) to get the information you need"
	echo
	
}
## END OF HELP ##
############################################

## Display help if -h is used
while getopts ":h" option; do
   case $option in
	h) # display Help
		Help
		exit;;
   esac
done

# set okta domain
domain=DOMAIN

## Base URL for okta instance, will read the relative URL from $1 input at run time e.g. /api/v1/users
url="https://${domain}.okta.com${1}"

## This will read your okta token in your environment file
token="${OKTA_TOKEN}"

## start loop while URL, so will paginate thru
while [ "$url" ];
do
	request=$( curl --compressed -Ss -i -H "authorization: SSWS $token" "$url" | tr -d '\r' )
	## Get body of response and output as a CSV to downloads
	## Output all json keys to a CSV with keys as column titles
	echo "$request" | sed '1,/^$/d' | jq -r '(. | map(leaf_paths) | unique) as $cols | map (. as $row | ($cols | map(. as $col | $row | getpath($col)))) as $rows | ([($cols | map(. | map(tostring) | join(".")))] + $rows) | map(@csv) | .[]' >> ~/Downloads/okta-export.csv
	## Get headers and read if theres another page link
	url=$( echo "$request" | sed -n -E 's/link: <(.*)>; rel="next"/\1/pi' )
done

echo "Export in Downloads"