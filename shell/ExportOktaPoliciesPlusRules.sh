#!/bin/zsh

## this will make a folder for each authentication policy, and then drop each rule for that policy inside it as a json


# set okta domain here
domain="your-okta-domain"

## Set field seperator to a comma
IFS=","

## Check for $OKTA_TOKEN in env variable otherwise ask for an okta API token
if [[ $OKTA_TOKEN == "" ]];
	then
	echo "no Okta token found."
	read -p "enter your okta api token to proceed: " OKTA_TOKEN
	echo "using okta API token $OKTA_TOKEN"
fi


## Read token as OMG_TOKEN from env file
token="${OKTA_TOKEN}"


# creat the folder to house all this
mkdir ~/Downloads/"Okta Auth Policies"

## Export all auth policies
policyList=$( curl --location -s --request GET 'https://'"${domain}"'.okta.com/api/v1/policies?type=ACCESS_POLICY&limit=150' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: SSWS '"$token"''  | jq -r '.[] | [.id, .name] | @csv' )

# read thru each line and make a folder for the name and get the rules

while read -r policy name
do
	folderName=$( echo "$name" | tr -d "\"" )
	# make a folder for the policy
	mkdir ~/Downloads/"Okta Auth Policies"/"${folderName}"
	
	policyID=$( echo "$policy" | tr -d "\"" )
	
	## get the list of ruleID for each policy
	ruleList=$( curl -s --location --request GET 'https://'"${domain}"'.okta.com/api/v1/policies/'"$policyID"'/rules' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: SSWS '"$token"'' | jq -r '.[] | [.id] | @csv' )

	while read -r rule
	do
		ruleID=$( echo "$rule" | tr -d "\"" )
		# get the rule itself
		ruleObject=$( curl -s --location --request GET 'https://'"${domain}"'.okta.com/api/v1/policies/'"$policyID"'/rules/'"$ruleID"'' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: SSWS '"$token"'' ) 
		
		# get the name
		ruleName=$( echo $ruleObject | jq -r '.name' )
		# get priority
		priority=$( echo $ruleObject | jq -r '.priority' )
		# combine so they show in the order in files sort
		ruleFileName=$( echo "$priority-$ruleName" )
		
		#export the rule object to the folder
		echo "$ruleObject" | jq >> ~/Downloads/"Okta Auth Policies"/"${folderName}"/"$ruleFileName".json
		
	done <<< $ruleList
	
done <<< $policyList

echo "export folder in downloads"