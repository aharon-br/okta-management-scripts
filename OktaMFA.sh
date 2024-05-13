#!/bin/sh

## version 1.51, apr 23, last edit harry r

## make this script executable "chmod +x /path/to/script.sh"

## help can be shown with "OktaMFA -help"

## run using a csv list of email addresses as the $1 input for this so "./ThisScript.sh /path/to/csv/emails.csv"

## this needs jq installed, homebrew can install with "brew install jq"

## this uses the env variable $OKTA_TOKEN for API token for ease of used, if that isn't set, just sub out that for your API token


############################################
## HELP ##
Help()
{
	# Display Help
	echo "Takes a list of emails in single column CSV"
	echo
	echo "Syntax: OktaMFA /path/to/list.csv"
	echo
	echo "Large exports may take a few minutes"
	echo "Try using cskvit (csvcut or csvgrep) to get the information you need"
	echo
	
}

## Display help if -h is used
while getopts ":h" option; do
   case $option in
	h) # display Help
		Help
		exit;;
   esac
done

## END OF HELP ##
############################################


### Perform Checks to proceed ####

if [[ $1 == "" ]];
	then
	echo "No input CSV specified. Displaying: OktaMFA -help"
	echo 
	echo "Takes a list of emails in single column CSV"
	echo
	echo "Syntax: OktaMFA /path/to/list.csv"
	echo
	echo "Large exports may take a few minutes"
	echo "Try using cskvit (csvcut or csvgrep) to get the information you need"
	echo
	exit 0
fi

## Check for OKTA_TOKEN
if [[ $OKTA_TOKEN == "" ]];
	then
	echo "no okta token found."
	read -p "enter your okta api token to proceed: " OKTA_TOKEN
	echo "using okta API token $OKTA_TOKEN"
fi


## Check if JQ is installed
if [ ! -d /usr/local/Cellar/jq ];
	then
	echo "jq isn't installed. this relies on jq.
	please install with "brew install jq""
	exit 0
fi

### End of checks ###

## Start run

# set okta domain
domain=DOMAIN

## Create a CSV in downloads with the column headers
echo "email,type,name,enrolled,last_used" >> ~/Downloads/MFA-report.csv

## read email and start loop
while read -r email

do
	## get user ID from the email and have as variable $userID
	userID=$( curl -s --location --request GET 'https://'"${domain}"'.okta.com/api/v1/users?q='"$email"'&limit=1' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: SSWS '"$OKTA_TOKEN"'' | jq '.[]|.id' | tr -d "\"" )

	## use /factors in okta user api to list the factors, use jq to extract factorType,authenticatorName,created,lastVerified
	## add in the email at the start of each line
	## output to MFA report in downloads
	curl -s --location --request GET 'https://'"${domain}"'.okta.com/api/v1/users/'"${userID}"'/factors' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: SSWS '"$OKTA_TOKEN"'' 2>/dev/null | jq '.[] | [.factorType,.profile.authenticatorName,.created,.lastVerified] | @csv' 2>/dev/null | tr -d "\\" | tr -d "\"" | sed -e 's/^/'"${email}"',/' >> ~/Downloads/MFA-report.csv 

done < $1

## Check if csvkit is installed, and cut a webauthn only version
if [ ! -d /usr/local/Cellar/csvkit ];
	then
		echo "csvkit isn't installed. cannot create webauthn filtered version
		please install with "brew install csvkit""
		echo
		echo "unfiltered export in Downloads folder"
		exit 0
	
	else
		cat ~/Downloads/MFA-report.csv | csvgrep -c type -m "webauthn" >> ~/Downloads/MFA-Report-webauthn-only.csv
		echo "Exports of full and webauthn filtered in Downloads"
fi