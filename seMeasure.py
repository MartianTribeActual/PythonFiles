#this app get stories and tasks associated with an epic
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
import os
import datetime
from datetime import timedelta
import json
import sys
import importlib

colors = importlib.import_module("modules.colors")
appManager = importlib.import_module('modules.appManager')

am = appManager.AppManager()
cm = colors.ColorManager()

rootURL = "https://kargo1.atlassian.net"

##############################################
# functions
##############################################

def getSECount(jira, range):

	#while startAt < 1001:
 
	print(f"{cm.OKGREEN}Getting SE tickets from {range['start']} to {range['end']}{cm.ENDC}")

	#search for issues
	results = jira.search_issues(f"project=SE&created>{range['start']}&created<{range['end']}&summary~'K-Pixel'&description~'K-Pixel'", maxResults=0, startAt=0, json_result=True)
	print(results)

##############################################
# app starts here
##############################################

#jira setup
print(f"{cm.OKGREEN}Getting Jira authentication JQL...{cm.ENDC}")
jiraOptions = {'server': rootURL}
jira = JIRA(options=jiraOptions,
    basic_auth=("ssuranie@kargo.com", "KqXtK3YEJCSMtSw1zbSN8456"),  # Jira Cloud: a username/token tuple
)

getSECount(jira, {"start": "2023-09-01", "end": "2023-10-15"})

