#!/bin/zsh


## Export app list from okta and combine as a CSV

## $ORG_NAME and $OKTA_TOKEN can be added to env file to save editing 

## Base URL for okta instance with the apps API
url="https://${ORG_NAME}.okta.com/api/v1/apps"

token="${OKTA_TOKEN}"

## Create csv with headers 
echo "id,label,status,signOnMode,features" >> ~/Downloads/okta-apps-export.csv

## start loop while URL, so will paginate thru
while [ "$url" ];
do
	request=$( curl --compressed -Ss -i -H "authorization: SSWS $token" "$url" | tr -d '\r' )
	## Get body of response and output as a CSV to downloads
	echo "$request" | sed '1,/^$/d' | jq -r '.[] | [.id,.label,.status,.signOnMode,.features[]] | join(",")' >> ~/Downloads/okta-apps-export.csv
	## Get headers and read if theres another page link
	url=$( echo "$request" | sed -n -E 's/link: <(.*)>; rel="next"/\1/pi' )
done

echo "Export in Downloads"