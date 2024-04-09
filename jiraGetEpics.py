from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
import importlib

colors = importlib.import_module("modules.colors")
appManager = importlib.import_module('modules.appManager')
googleManager = importlib.import_module('modules.googleManager')

am = appManager.AppManager()
cm = colors.ColorManager()
gm = googleManager.GoogleManager()

rootAPIURL = "https://kargo1.atlassian.net/rest/api/2/search?jql="
rootURL = "https://kargo1.atlassian.net"

##############################################
# functions
##############################################

def getEpics():

	print(f"{cm.OKGREEN}Getting Jira Epics...{cm.ENDC}") 

	lstBoards = ["KME", "DEAL", "KAT", "KVID", "CM", "CTV", "KRKPD", "KDW", "WEB"]
	lstDates = getEpicDates()
	dictEpics = {}

	for thisBoard in lstBoards:
		strJQL = f"project={thisBoard} AND created > {lstDates[0]} AND created < {lstDates[1]} AND issuetype='Epic'"
		lstIssues = jira.search_issues(strJQL, maxResults=250)
		dictEpics[thisBoard] = lstIssues
		
	return dictEpics

def getEpicDates():

	strYear = datetime.now().year
	Q1S = f"{strYear}-01-01"
	Q1E = f"{strYear}-03-31"
	Q2S = f"{strYear}-04-01"
	Q2E = f"{strYear}-06-30"
	Q3S = f"{strYear}-07-01"
	Q3E = f"{strYear}-09-30"
	Q4S = f"{strYear}-10-01"
	Q4E = f"{strYear}-12-31"

	#get the quarter
	try:
		lstDtsToCheck = []
		isDtToCheck = am.dateIsBetweenDates(datetime.now(), datetime.strptime(Q1S, "%Y-%m-%d"), datetime.strptime(Q1E, "%Y-%m-%d"))
		if isDtToCheck: 
			lstDtsToCheck.extend([Q1S, Q1E])

		isDtToCheck = am.dateIsBetweenDates(datetime.now(), datetime.strptime(Q2S, "%Y-%m-%d"), datetime.strptime(Q2E, "%Y-%m-%d"))
		if isDtToCheck: 
			lstDtsToCheck.extend([Q2S, Q2E])

		isDtToCheck = am.dateIsBetweenDates(datetime.now(), datetime.strptime(Q3S, "%Y-%m-%d"), datetime.strptime(Q3E, "%Y-%m-%d"))
		if isDtToCheck: 
			lstDtsToCheck.extend([Q3S, Q3E])

		isDtToCheck = am.dateIsBetweenDates(datetime.now(), datetime.strptime(Q4S, "%Y-%m-%d"), datetime.strptime(Q4E, "%Y-%m-%d"))
		if isDtToCheck: 
			lstDtsToCheck.extend([Q4S, Q4E])

		if len(lstDtsToCheck) == 2: 
			return lstDtsToCheck
		else:
			print(f"{cm.WARNING}Something went wrong with getting the epic date range.{cm.ENDC}")

	except Exception as e: 
		print(f"{cm.WARNING}{e}{cm.ENDC}")

def createEpicData(dictEpics):

	print(f"{cm.OKGREEN}Creatng spreadsheet data...{cm.ENDC}")

	lstData = [["Board", "Epic", "Summary", "Status", "Link"]]

	try: 
		for thisKey in dictEpics:
			lstIssues = dictEpics[thisKey]

			for thisIssue in lstIssues: 
				strSummary = thisIssue.fields.summary
				strStatus = thisIssue.fields.status
				strDescription = thisIssue.fields.description
				strLink = f"https://kargo1.atlassian.net/browse/{thisIssue.key}"

				lstData += [thisKey, thisIssue.key, strSummary, strStatus, strLink]

	except Exception as e: 
		print(f"{cm.WARNING}{e}{cm.ENDC}")


	if len(lstData) > 1: 
		return lstData
	else: 
		print(f"{cm.WARNING}There was an issue getting the epic lists{cm.ENDC}")

def getGoogleServices(): 

    bSuccess = True
    strErr = ""

    #authenticate into Google
    print(f"{cm.OKGREEN}Authenticating with Google..{cm.ENDC}")
    dictResults = gm.getAuth()

    #if authentication fails
    if dictResults["success"] == False: 
        bSuccess = False
        strErr += f"\n{cm.WARNING}{dictResults['error-message']}{cm.ENDC}"
    else: 
        creds = dictResults["credentials"]

    #get gmail service
    dictGmailResults = gm.getService(creds,0)
    if dictGmailResults["success"] == False:
        bSuccess = False
        strErr += f"\n{cm.WARNING}{dictGmailResults['error-message']}{cm.ENDC}"
    else: 
        gmailService = dictGmailResults["service"]

    #get sheets service
    dictSheetsResults = gm.getService(creds, 1)
    if dictSheetsResults["success"] == False:
        bSuccess = False
        strErr += f"\n{cm.WARNING}{dictSheetsResults['error-message']}{cm.ENDC}"
    else: 
        sheetsService = dictSheetsResults["service"]

        return {"success":bSuccess, "gmail-service":gmailService, "sheets-service":sheetsService, "error-message": strErr}


def updateSheet(service, lstEpics):




##############################################
# app starts here
##############################################

#jira setup
print(f"{cm.OKGREEN}Getting Jira authentication JQL...{cm.ENDC}")
jiraOptions = {'server': "https://kargo1.atlassian.net"}
jira = JIRA(options=jiraOptions,
    basic_auth=("ssuranie@kargo.com", "KqXtK3YEJCSMtSw1zbSN8456"),  # Jira Cloud: a username/token tuple
)

dictEpics = getEpics()

dictGoogleServices = getGoogleServices()
if dictGoogleServices["success"] == False:
    print(dictGoogleServices["error-message"])
else: 
    sheetsService = dictGoogleServices["sheets-service"]
    updateSheet(sheetsService, createEpicData(dictEpics))
