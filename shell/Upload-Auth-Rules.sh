#!/bin/zsh

## takes the edited rule objects exported, once edited as needed and uploads them
## working on assumption the folder is still the same name and location - edit if needed


# set okta domain here e.g. if domain is acme.okta.com, enter acme 
domain="your-okta-domain"

## Check for $OKTA_TOKEN in env variable otherwise ask for an okta API token
if [[ $OKTA_TOKEN == "" ]];
	then
	echo "no Okta token found."
	read -p "enter your okta api token to proceed: " OKTA_TOKEN
	echo "using okta API token $OKTA_TOKEN"
fi


## Read token as OMG_TOKEN from env file
token="${OKTA_TOKEN}"

## get a csv of all the policy name + ID
policyCSV=$( curl -s --location --request GET 'https://'"${domain}"'.okta.com/api/v1/policies?type=ACCESS_POLICY' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: SSWS '"$token"'' | jq -r '.[] | [.id,.name] | @csv' )

# get the list of policys from the export folder
policyList=$( ls ~/Downloads/"Okta Auth Policies" )

# read thru each one
while read -r policyName
do
	# get policy ID
	policyID=$( echo "$policyCSV"| grep "${policyName}" | awk -F , '{print $1}' | tr -d "\"" )
	
	# get the rules
	ruleList=$( ls ~/Downloads/"Okta Auth Policies"/"${policyName}" )
	
	# read thru each one
	while read ruleFileName
	do
		# get the file path
		ruleLocation="~/Downloads/""Okta Auth Policies""/"${policyName}"/"${ruleFileName}""
		
		# get the rule ID
		ruleID=$( jq -r '.id' ${ruleLocation} )
		
		# get the name
		ruleName=$( jq -r '.name' ${ruleLocation} )
		
		# get the data for the body
		ruleData=$( jq '.' ${ruleLocation} )
		
		## update the rule with the body filled the json file
		curl -s --location --request PUT 'https://'"${domain}"'.okta.com/api/v1/policies/'"${policyID}"'/rules/'"${ruleID}"'' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--header 'Authorization: SSWS '"$token"'' \
--data ''"${ruleData}"'' >> /dev/null
		
		echo "$ruleName in $policyName is uploaded"

	done <<< $ruleList

done <<< $policyList

echo "all complete"