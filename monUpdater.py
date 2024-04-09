#this script is a POC to write to a Monday board: 
import os
from datetime import datetime
from datetime import timedelta
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
import requests
import json
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
dictStatusMap = {'KME': {'open': ['Open'], 'qa': ['In QA - DEV', 'In QA - STG'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Closed']}, 
'DEAL': {'open': ['To Do'], 'qa': ['QA', 'Ready for QA', 'In QA'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Closed']}, 
'KAT': {'open': ['Open'], 'qa': ['In QA - DEV'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Closed']}, 
'KVID': {'open': ['To Do'], 'qa': ['Ready for QA'], 'in-dev': ['In Progress'], 'on-hold': [], 'code-review': ['Code Review', 'In Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Done']}, 
'CM': {'open': ['Open'], 'qa': ['QA'], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready for Release'], 'closed': ['Done']}, 
'CTV': {'open': ['To Do'], 'qa': ['In QA'], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 
'KDW': {'open': ['Open'], 'qa': ['In QA - STG'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 
'WEB': {'open': ['To Do'], 'qa': ['In QA'], 'in-dev': ['In DEV'], 'on-hold': ['On Hold / Need more Info', 'Backlog'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Closed']}, 
'PEG': {'open': ['To Do'], 'qa': [], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 
'KRKPD': {'open': ['Open', 'Design / Planning'], 'qa': ['In QA', 'Ready for QA'], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 
'KRAK': {'open': ['Open'], 'qa': ['QA'], 'in-dev': ['In Progress'], 'on-hold': ['On Hold / Need more Info'], 'code-review': ['Code Review'], 'ready-for-release': [], 'closed': ['Done']}, 
'ZIG': {'open': ['To Do'], 'qa': [], 'in-dev': ['In Progress'], 'on-hold': ['On Hold/Blocked'], 'code-review': [], 'ready-for-release': [], 'closed': ['Done']}, 
'BRAIN': {'open': ['Backlog', 'Up Next'], 'qa': ['In QA'], 'in-dev': ['In Progress'], 'on-hold': ['On Hold/Needs More Info'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready For Release'], 'closed': ['Done']}, 
'IT': {'open': ['Open'], 'qa': ['Ready for QA(2)'], 'in-dev': ['In Development'], 'on-hold': ['On Hold', 'Paused', 'Blocked'], 'code-review': ['In PR'], 'ready-for-release': [], 'closed': ['Done', 'Live']}, 
'CT': {'open': ['Open'], 'qa': ['Ready for QA(Migrated)'], 'in-dev': ['In Development'], 'on-hold': ['Rejected', 'Paused', 'Blocked'], 'code-review': ['In PR', 'Waiting for PR'], 'ready-for-release': [], 'closed': ['Done']}, 
'MB': {'open': ['Open'], 'qa': ['Ready for QA'], 'in-dev': ['In Development'], 'on-hold': ['Rejected', 'Blocked By Publisher', 'Blocked'], 'code-review': [], 'ready-for-release': [], 'closed': ['Done']}, 
'KA': {'open': ['New Request'], 'qa': ['Under Acceptance'], 'in-dev': ['In Dev'], 'on-hold': ['Blocked/Need Info'], 'code-review': ['Peer Review', 'Under Review', 'Under Technical Review'], 'ready-for-release': [], 'closed': ['Complete']}, 
'CERB': {'open': ['Open', 'Up Next'], 'qa': ['In QA - STG'], 'in-dev': ['In Dev'], 'on-hold': ['On Hold'], 'code-review': ['Code Review'], 'ready-for-release': ['Ready For Release'], 'closed': ['Done']}}

dictBoardIds = {"check":"Has No Point Stories", "text8":"Epic", "numbers0": "Ticket Count", "numbers9": "Total Epic Points", "dup__of_epic_points":"Not Started Points", "numeric":"In Progress Points", "numeric4":"Done Points", "numbers09":"Spike Ticket Count", "numbers3": "Spike Not Started Pts", "numbers53": "Spike In Dev Pts", "numbers2": "Spike Closed Pts", "numbers54": "Bug Ticket Count", "numbers1": "Bug Not Started Pts", "numbers64": "Bug In Dev Pts", "numbers4": "bugClosedPts"}

##########################
# FUNCTIONS              #
##########################

def getJiraEpics():

	print(f"{cm.OKGREEN}Getting Epics...{cm.ENDC}")

	lstAllEpics = []

	lstBoards = ["KME", "DEAL", "KAT", "KVID", "CMA", "KRKPD", "KRAK", "ZIG", "PEG", "KDW", "WEB"]
	#lstBoards = ["KRAK"]

	for thisBoard in lstBoards: 
		
		try:
			lstBoardStatuses = []
			strJQL = f"project={thisBoard} AND created >= '2023-12-01' AND issuetype='Epic' and status != 'closed'"
			#lstIssues = jira.search_issues(strJQL, maxResults=250)
			lstAllEpics.extend(jira.search_issues(strJQL, maxResults=250))

		except Exception as e: 
			print(f"{cm.WARNING}There was an issues getting the Jira epics for {thisBoard}\n{e}{cm.ENDC}")


	return lstAllEpics

def getQuarter(): 

	dtToday = datetime.now()
	currentQ = "Q5"
	if dtToday.month <= 3: 
		currentQ = "Q1"
	elif dtToday.month > 3 and dtToday.month <= 6:
		currentQ = "Q2"
	elif dtToday.month > 6 and dtToday.month <= 9:
		currentQ = "Q3"
	elif dtToday.month > 9 and dtToday.month <= 12:
		currentQ = "Q4"

	return currentQ

def getAllGroupIds(boardId): 

	print(f"{cm.OKGREEN}Getting Monday board groups...{cm.ENDC}")

	lstGroups = []

	try:
		dictResponse = mm.getAllGroups(boardId, mondayToken)
		
		lstGroups = dictResponse["boards"][0]["groups"]

	except Exception as e: 
		print(f"{cm.WARNING}There was an error getting the group ids for the board\n{e}{cm.ENDC}")

	return lstGroups

def getGroupItems(groupId): 

	#get all group items for product board
	print(f"{cm.OKGREEN}Getting Monday board items...{cm.ENDC}")

	dictBoards = mm.getAllGroupItems(boardId, groupId, mondayToken)
	lstItems = dictBoards["boards"][0]["groups"][0]["items_page"]["items"]
	
	return lstItems

def getEpicsFromItems(lstItems):

	print(f"{cm.OKGREEN}Getting Monday board epics...{cm.ENDC}")

	lstMonEpics = []

	for thisItem in lstItems: 

		lstCols = thisItem["column_values"]
		for thisCol in lstCols:
			if thisCol["id"] == "text8":
				lstMonEpics.append(thisCol["text"])

	return lstMonEpics


def getNewEpics(lstEpics, lstMonEpics):

	bStartOver = False
	lstNewEpics = []

	for idx, thisEpic in enumerate(lstEpics): 
		if thisEpic.key not in lstMonEpics: 
			lstNewEpics.append(thisEpic)
	
	if len(lstNewEpics) > 0:

		print(f"{cm.OKGREEN}New epics detected...{cm.ENDC}") 
		createAnItem(boardId, parseEpicData(lstNewEpics))
		bStartOver = True

	else: 
		print(f"{cm.OKGREEN}No new epics detected...{cm.ENDC}")

	return bStartOver

def getEpicStories(lstKeys):

	print(f"{cm.OKCYAN}Getting epic stories...{cm.ENDC}")
	lstEpicData = []
	lstCompletedEpics = []

	for thisKey in lstKeys:

		if thisKey not in lstCompletedEpics:

			try: 

				#filter for some empty strings that were coming back
				if len(thisKey) > 0:

					strBoard = str(thisKey.split("-")[0]).upper()

					dictBoardMap = dictStatusMap[strBoard]
					
					dictEpic = {}
					dictEpic["key"] = thisKey
					dictEpic["board"] = strBoard
					dictEpic["notStarted"] = 0
					dictEpic["inProg"] = 0
					dictEpic["closed"] = 0
					dictEpic["points"] = 0
					dictEpic["hasPoints"] = True

					dictEpic["ticket-count"] = 0
					dictEpic["story-ticket-count"] = 0
					dictEpic["spike-ticket-count"] = 0
					dictEpic["bug-ticket-count"] = 0

					dictEpic["spikeNotStarted"] = 0
					dictEpic["spikeInProg"] = 0
					dictEpic["spikeClosed"] = 0
					dictEpic["spikePoints"] = 0

					dictEpic["bugNotStarted"] = 0
					dictEpic["bugInProg"] = 0
					dictEpic["bugClosed"] = 0
					dictEpic["bugPoints"] = 0

					#create jql	to get stories of epic
					strJQL = f"project = {strBoard} and parentEpic in ({thisKey}) and issueType != 'epic' and issueType != 'sub-task'"
					lstIssues = jira.search_issues(strJQL, maxResults=250)

					if len(lstIssues) > 0:

						dictEpic["ticket-count"] = len(lstIssues)
						myPoints = 0

						#loop through each story of epic, get its points, aggregate to epic total and add to specific status
						for thisIssue in lstIssues:

							mySpikePoints = 0
							myBugPoints = 0
							myStoryPoints = 0
							bHasPoints = False

							strType = str(thisIssue.fields.issuetype)
							strStatus = str(thisIssue.fields.status)

							#update ticket counts
							if strType == "Story" or "Task": 
								dictEpic["story-ticket-count"] += 1

							if strType == "Spike":
								dictEpic["spike-ticket-count"] += 1
							
							if strType == "Bug":
								dictEpic["bug-ticket-count"] += 1

							#aggregate all points

							if "customfield_11200" in list(dir(thisIssue.fields)):
								if thisIssue.fields.customfield_11200 is not None:
									bHasPoints = True
									dictEpic["points"] += int(thisIssue.fields.customfield_11200)
									myPoints += int(thisIssue.fields.customfield_11200)
									myStoryPoints = int(thisIssue.fields.customfield_11200)
							if bHasPoints == False and "customfield_10005" in list(dir(thisIssue.fields)):
								if thisIssue.fields.customfield_10005 is not None: 
									bHasPoints = True
									dictEpic["points"] += int(thisIssue.fields.customfield_10005)
									myPoints += int(thisIssue.fields.customfield_10005)
									myStoryPoints = int(thisIssue.fields.customfield_10005)
							if bHasPoints == False and "customfield_13656" in list(dir(thisIssue.fields)):
								if thisIssue.fields.customfield_13656 is not None: 
									bHasPoints = True
									dictEpic["points"] += int(thisIssue.fields.customfield_13656)
									myPoints += int(thisIssue.fields.customfield_13656)
									myStoryPoints = int(thisIssue.fields.customfield_13656)

							#aggregate spike points
							if strType == "Spike":
								if "customfield_11200" in list(dir(thisIssue.fields)):
									bHasPoints = True
									if thisIssue.fields.customfield_11200 is not None: 
										dictEpic["spikePoints"] += int(thisIssue.fields.customfield_11200)
										mySpikePoints += int(thisIssue.fields.customfield_11200)
								if "customfield_10005" in list(dir(thisIssue.fields)):
									bHasPoints = True
									if thisIssue.fields.customfield_10005 is not None: 
										dictEpic["spikePoints"] += int(thisIssue.fields.customfield_10005)
										mySpikePoints += int(thisIssue.fields.customfield_10005)
								if "customfield_13656" in list(dir(thisIssue.fields)):
									bHasPoints = True
									if thisIssue.fields.customfield_13656 is not None: 
										dictEpic["spikePoints"] += int(thisIssue.fields.customfield_13656)
										mySpikePoints += int(thisIssue.fields.customfield_13656)

							#aggregate story points
							if strType == "Bug":
								if "customfield_11200" in list(dir(thisIssue.fields)):
									bHasPoints = True
									if thisIssue.fields.customfield_11200 is not None: 
										dictEpic["bugPoints"] = int(thisIssue.fields.customfield_11200)
										myBugPoints += int(thisIssue.fields.customfield_11200)
								if "customfield_10005" in list(dir(thisIssue.fields)):
									bHasPoints = True
									if thisIssue.fields.customfield_10005 is not None: 
										dictEpic["bugPoints"] = int(thisIssue.fields.customfield_10005)
										myBugPoints += int(thisIssue.fields.customfield_10005)
								if "customfield_13656" in list(dir(thisIssue.fields)):
									bHasPoints = True
									if thisIssue.fields.customfield_13656 is not None:
										dictEpic["bugPoints"] = int(thisIssue.fields.customfield_13656)
										myBugPoints += int(thisIssue.fields.customfield_13656)

							#point check
							dictEpic["hasPoints"] = bHasPoints
							
							#set points for statuses
							if strType == "Story" or strType == "Task":
								if strStatus in dictBoardMap["open"]:
									dictEpic["notStarted"] += myStoryPoints
								elif strStatus in dictBoardMap["qa"] :
									dictEpic["inProg"] += myStoryPoints
								elif strStatus in dictBoardMap["in-dev"]:
									dictEpic["inProg"] += myStoryPoints
								elif strStatus in dictBoardMap["on-hold"]:
									dictEpic["inProg"] += myStoryPoints
								elif strStatus in dictBoardMap["code-review"]:
									dictEpic["inProg"] += myStoryPoints
								elif strStatus in dictBoardMap["ready-for-release"]:
									dictEpic["inProg"] += myStoryPoints
								elif strStatus in dictBoardMap["closed"]:
									dictEpic["closed"] += myStoryPoints
							
							if strType == "Spike":
								if strStatus in dictBoardMap["open"]:
									dictEpic["spikeNotStarted"] += mySpikePoints
								elif strStatus in dictBoardMap["qa"] :
									dictEpic["spikeInProg"] += mySpikePoints
								elif strStatus in dictBoardMap["in-dev"]:
									dictEpic["spikeInProg"] += mySpikePoints
								elif strStatus in dictBoardMap["on-hold"]:
									dictEpic["spikeInProg"] += mySpikePoints
								elif strStatus in dictBoardMap["code-review"]:
									dictEpic["spikeInProg"] += mySpikePoints
								elif strStatus in dictBoardMap["ready-for-release"]:
									dictEpic["spikeInProg"] += mySpikePoints
								elif strStatus in dictBoardMap["closed"]:
									dictEpic["spikeClosed"] += mySpikePoints

							if strType == "Bug":
								if strStatus in dictBoardMap["open"]:
									dictEpic["bugNotStarted"] += myBugPoints
								elif strStatus in dictBoardMap["qa"] :
									dictEpic["bugInProg"] += myBugPoints
								elif strStatus in dictBoardMap["in-dev"]:
									dictEpic["bugInProg"] += myBugPoints
								elif strStatus in dictBoardMap["on-hold"]:
									dictEpic["bugInProg"] += myBugPoints
								elif strStatus in dictBoardMap["code-review"]:
									dictEpic["bugInProg"] += myBugPoints
								elif strStatus in dictBoardMap["ready-for-release"]:
									dictEpic["bugInProg"] += myBugPoints
								elif strStatus in dictBoardMap["closed"]:
									dictEpic["bugClosed"] += myBugPoints

				lstEpicData.append(dictEpic)
				lstCompletedEpics.append(thisKey)

			except Exception as e: 
				print(f"{cm.WARNING}There was an issues getting data for the epic: {thisKey}\n{e}{cm.ENDC}")


	return lstEpicData

def updateMondayBoard(lstEpics):

	print(f"{cm.OKGREEN}Updating item data in Monday...{cm.ENDC}")

	lstErrors = [] 
	strBody = f"There were some errors with the Monday Updater on {str(datetime.now().month)}-{str(datetime.now().day)}-{str(datetime.now().year)}\n"

	for thisEpic in lstEpics:

			try:

				#set up data to pass
				# dictUpdateData = {"numbers9": thisEpic["points"], "dup__of_epic_points": thisEpic["notStarted"], "numeric":thisEpic["inProg"], "numeric4":thisEpic["closed"]}

				dictHeader = {'Content-Type': 'application/json', "Authorization":mondayToken, 'API-Version' : '2024-01'}
				mondayURL = "https://api.monday.com/v2"

				#get item id
				dictItemData = mm.getItemIdByColValue(boardId, "text8", thisEpic["key"])
				monItemId = dictItemData["items_page_by_column_values"]["items"][0]["id"]
				
				myVars = {
					"boardId": boardId,
					"itemId": int(monItemId),
					"columnVals": json.dumps({
						"numbers9":thisEpic["points"],
						"dup__of_epic_points": thisEpic["notStarted"],
						"numeric": thisEpic["inProg"],
						"numeric4": thisEpic["closed"],
						"numbers0": thisEpic["ticket-count"],
						"numbers3": thisEpic["spikeNotStarted"], 
						"numbers53": thisEpic["spikeInProg"], 
						"numbers2": thisEpic["spikeClosed"], 
						"numbers1": thisEpic["bugNotStarted"], 
						"numbers64": thisEpic["bugInProg"], 
						"numbers4": thisEpic["bugClosed"],
						"numbers54": thisEpic["bug-ticket-count"],
						"numbers09": thisEpic["spike-ticket-count"]
					})
				}

				itemId = myVars["itemId"]
				columns = myVars["columnVals"]

				query = "mutation ($boardId: ID!, $itemId: ID!, $columnVals: JSON!) { change_multiple_column_values(board_id:$boardId, item_id:$itemId, column_values:$columnVals) { id } }"

				data = {'query': query, 'variables': myVars}
				r = requests.post(url=mondayURL, json=data, headers=dictHeader) 

			except Exception as e:
				print (f"{cm.WARNING}There was an error updating Monday:\n{e}{cm.ENDC}")
				return {"item":itemId, "error":e}

	sendGmail({"to":["ssuranie@kargo.com"], "subject":"Monday Update Has Finished", "body": f"The {str(datetime.now().hour)}:00 Monday Board Update for {str(datetime.now().year)}-{str(datetime.now().month)}-{str(datetime.now().day)} has completed. There were {str(len(lstErrors))} detected."})


def parseEpicData(lstEpics):

	print(f"{cm.OKGREEN}Parsing epic data...{cm.ENDC}") 

	lstMaster = []

	try:
		for thisEpic in lstEpics: 

			dictThisEpic = {"key":thisEpic.key, "summary":thisEpic.fields.summary, "timeestimate":thisEpic.fields.aggregatetimeestimate, "timespent":thisEpic.fields.aggregatetimespent, "start-date": getattr(thisEpic.fields, 'customfield_ 13628', "")}

			lstMaster.append(dictThisEpic)
			
	except Exception as e: 
			print(f"{cm.WARNING}There was an issues getting the Jira epics details for: {thisEpic}\n{e}{cm.ENDC}")

	return lstMaster

def createAnItem(boardId, lstEpics):

	print(f"{cm.OKGREEN}Creating Monday items..{cm.ENDC}") 

	lstEpicKeys = []

	for thisEpic in lstEpics:
		dictData = {}
		itemName = thisEpic["summary"]
		dictData["epic"] = thisEpic['key']
		lstEpicKeys.append(thisEpic['key'])
		mm.createItem(boardId, itemName, dictData, itemType.E, mondayToken)

		strBody = f"The following epics were added to the Monday board:\n"
		for thisKey in lstEpicKeys:
			strBody += f"{thisKey}\n"
		strBody += f"\n\n"

		#sendGmail({"to":["ssuranie@kargo.com", "puneet@kargo.com", "max.dowaliby@kargo.com", "meghan.gabaly@kargo.com"], "subject":"New Epics Added To Monday Board", "body": strBody})

def sendGmail(dictMailData):

	print(f"{cm.OKGREEN}Authenticating with Google..{cm.ENDC}")
	dictResults = gm.getAuth()

	if dictResults["success"] == False: 
		print(f"{cm.WARNING}There was an error autheticating into Google! \n{dictResults['error-message']}{cm.ENDC}")
	else: 

		print(f"{cm.OKGREEN}Successful Google Auth..{cm.ENDC}")
		creds = dictResults["credentials"]
		
		bSuccess = True
		dictGmailResults = gm.getService(creds,0)
		if dictGmailResults["success"] == False:
			bSuccess = False
			strErr += f"\n{cm.WARNING}{dictGmailResults['error-message']}{cm.ENDC}"
		else: 
			gmailService = dictGmailResults["service"]

		if bSuccess == False: 
			print(strErr)
		else:

			for thisRecipient in dictMailData["to"]:

				message = MIMEText(dictMailData["body"])
				message['to'] = thisRecipient
				message['subject'] = dictMailData["subject"]
				create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

				try:
					message = (gmailService.users().messages().send(userId="me", body=create_message).execute())
					print(f'{cm.OKCYAN}Sent message to {message} Message Id: {message["id"]}{cm.ENDC}')
				except HTTPError as error:
					print(f'{cm.WARNING}An error occurred: {error}')
					message = None




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

	lstAllEpics = getJiraEpics()
	currentQ = getQuarter()
	lstGroups = getAllGroupIds(boardId)

	for idx, thisGroup in enumerate(lstGroups):
		if currentQ in thisGroup["title"]:
			lstItems = getGroupItems(thisGroup["id"])
			lstMonEpics = getEpicsFromItems(lstItems)

			bStartOver = getNewEpics(lstAllEpics, lstMonEpics)
			if bStartOver == True: 
				lstItems = getGroupItems(thisGroup["id"])
				lstMonEpics = getEpicsFromItems(lstItems)
				
			lstEpicData = getEpicStories(lstMonEpics)
			updateMondayBoard(lstEpicData)

			

