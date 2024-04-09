#this script is a POC to write to a Monday board: 
import os
from datetime import datetime
from datetime import timedelta
import importlib
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
from enum import Enum
import base64
from email.mime.text import MIMEText
from requests import HTTPError
import importlib

# import modules from relative paths
colors = importlib.import_module('modules.colors')
mondayManager = importlib.import_module('modules.mondayManager')
appManager = importlib.import_module('modules.appManager')
googleManager = importlib.import_module('modules.googleManager')

class pointSource(Enum):
	field1 = "customfield_11200"
	field2 = "customfield_10005"
	field3 = "customfield_13656"


class errorType(Enum):
	err1 = "Getting Jira Ticket"
	err2 = "Getting Jira Stories"
	err3 = "Prepping Content for Monday Update"
	err4 = "Updating Monday Board"

#steve suranie's token, should be changed to a pseudo user
mondayToken = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI1NjE0ODAwMCwiYWFpIjoxMSwidWlkIjoyNzg1NTcwMSwiaWFkIjoiMjAyMy0wNS0xMlQxNTo0ODoyOS4wMDBaIiwicGVyIjoibWU6d3JpdGUiLCJhY3RpZCI6MjU2NTg3NywicmduIjoidXNlMSJ9.zv6JlQh03iYpzlQjf9bVPLHZ19DJHY6G7lsE4bPF4QQ"

mm = mondayManager.MondayManager(mondayToken)
am = appManager.AppManager()
cm = colors.ColorManager()
gm = googleManager.GoogleManager()

service = None
creds = None

itemType = mondayManager.itemType

rootAPIURL = "https://kargo1.atlassian.net/rest/api/2/search?jql="
rootURL = "https://kargo1.atlassian.net"

boardId = 4457668941

#status mapper
dictStatusMap = {'KME': {'open': ['Open'], 'qa': ['In QA - DEV', 'In QA - STG'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Closed']}, 'DEAL': {'open': ['To Do'], 'qa': ['QA', 'Ready for QA', 'In QA'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Closed']}, 'KAT': {'open': ['Open'], 'qa': ['In QA - DEV'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Closed']}, 'KVID': {'open': ['To Do'], 'qa': ['Ready for QA'], 'in-dev': ['In Progress'], 'on-hold': [], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Done']}, 'CM': {'open': ['Open'], 'qa': ['QA'], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Done']}, 'CTV': {'open': ['To Do'], 'qa': ['In QA'], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 'KDW': {'open': ['Open'], 'qa': ['In QA - STG'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 'WEB': {'open': ['To Do'], 'qa': ['In QA'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold / Need more Info', 'Backlog'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Closed']}, 'PEG': {'open': ['To Do'], 'qa': [], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 'KRKPD': {'open': ['Open'], 'qa': ['In QA', 'Ready for QA'], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 'KRAK': {'open': ['Open'], 'qa': [], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 'ZIG': {'open': ['To Do'], 'qa': [], 'in-dev': ['In Progress'], 'on-hold': ['On Hold/Blocked'], 'code-review': [], 'ready-for-release': [], 'closed': ['Done']}}

dictBoardIds = {"check":"Has No Point Stories", "text8":"Epic", "numbers9": "Total Epic Points", "dup__of_epic_points":"Not Started Points", "numeric":"In Progress Points", "numeric4":"Done Points"}

##########################
# FUNCTIONS              #
##########################

def getAnEpic(strKey):

	try: 
		strJQL = f"key={strKey}"
		lstIssues = jira.search_issues(strJQL, maxResults=250)
	except Exception as e: 
		print(f"{cm.WARNING}There was an issues getting the Jira epics for {thisBoard}\n{e}{cm.ENDC}")

	return lstIssues

def getEpicStories(lstKeys):

	print(f"{cm.OKGREEN}Getting epic stories...{cm.ENDC}")
	lstEpicData = []

	for thisKey in lstKeys:

		try: 

			strBoard = thisKey.split("-")[0]
			dictBoardMap = dictStatusMap[strBoard]
			
			dictEpic = {}
			dictEpic["key"] = thisKey
			dictEpic["board"] = strBoard
			dictEpic["notStarted"] = 0
			dictEpic["inProg"] = 0
			dictEpic["closed"] = 0
			dictEpic["points"] = 0
			dictEpic["hasPoints"] = True

			#create jql	to get stories of epic
			strJQL = f"project = {strBoard} and parentEpic in ({thisKey}) and issueType != 'epic'"
			lstIssues = jira.search_issues(strJQL, maxResults=250)

			if len(lstIssues) > 0: 

				#loop through each story of epic, get its points, aggregate to epic total and add to specific status
				for thisIssue in lstIssues:

					#get story points
					bHasPoints = False
					myPoints = 0
					if "customfield_11200" in list(dir(thisIssue.fields)):
						bHasPoints = True
						if thisIssue.fields.customfield_11200 is not None: 
							myPoints += int(thisIssue.fields.customfield_11200)
					if "customfield_10005" in list(dir(thisIssue.fields)):
						bHasPoints = True
						if thisIssue.fields.customfield_10005 is not None: 
							myPoints += int(thisIssue.fields.customfield_10005)
					if "customfield_13656" in list(dir(thisIssue.fields)):
						bHasPoints = True
						if thisIssue.fields.customfield_13656 is not None: 
							myPoints += int(thisIssue.fields.customfield_13656)
					
					dictEpic["hasPoints"] = bHasPoints

		 			#incrementing total points
					dictEpic["points"] += myPoints

					strStatus = str(thisIssue.fields.status)

					if strStatus in dictBoardMap["open"]:
						dictEpic["notStarted"] += myPoints
					elif strStatus in dictBoardMap["qa"] :
						dictEpic["inProg"] += myPoints
					elif strStatus in dictBoardMap["in-dev"]:
						dictEpic["inProg"] += myPoints
					elif strStatus in dictBoardMap["on-hold"]:
						dictEpic["inProg"] += myPoints
					elif strStatus in dictBoardMap["code-review"]:
						dictEpic["inProg"] += myPoints
					elif strStatus in dictBoardMap["ready-for-release"]:
						dictEpic["inProg"] += myPoints
					elif strStatus in dictBoardMap["closed"]:
						dictEpic["closed"] += myPoints

			lstEpicData.append(dictEpic)
				
		except Exception as e: 
			print(f"{cm.WARNING}There was an issues getting data for the epic: {thisKey}\n{e}{cm.ENDC}")
				

	return lstEpicData

##########################
# APP STARTS HERE       #
##########################

if __name__ == "__main__": 

	print(f"{cm.OKCYAN}App is starting...{cm.ENDC}")

	#jira setup
	print(f"{cm.OKGREEN}Getting Jira authentication JQL...{cm.ENDC}")
	jiraOptions = {'server': "https://kargo1.atlassian.net"}
	# Jira Cloud: a username/token tuple
	jira = JIRA(options=jiraOptions, basic_auth=("ssuranie@kargo.com", "KqXtK3YEJCSMtSw1zbSN8456"))

	lstIssues = getAnEpic("KAT-5512")
	strKey = lstIssues[0].key
	dictEpics = getEpicStories([strKey])
	print(dictEpics)


	