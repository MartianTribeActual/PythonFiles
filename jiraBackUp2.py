from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
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

##############################################
# functions
##############################################

def getIssues(thisBoard): 

	print(f"{cm.OKGREEN}Getting {thisBoard} Issues...{cm.ENDC}") 

	try:

		lstBoards = ["RA"]
		lstDates = ["2023-01-01", "2021-12-31"]

		#AND key = 'RA-1030' <= save for debugging
		for thisBoard in lstBoards:
			strJQL = f"project={thisBoard} AND created < {lstDates[1]}"
			lstIssues = jira.search_issues(strJQL, maxResults=0, startAt=0, expand='renderedBody')

		return lstIssues

	except Exception as e: 

		print(f"{cm.WARNING}There was an issue with getting the issue data for {thisIssue.key}{cm.ENDC}")

def getGoogleServices():

	print(f"{cm.OKGREEN}Getting Google services...{cm.ENDC}")
	

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

##############################################
# app starts here
##############################################

#jira setup
print(f"{cm.OKGREEN}Getting Jira authentication JQL...{cm.ENDC}")
jiraOptions = {'server': "https://kargo1.atlassian.net"}
jira = JIRA(options=jiraOptions,
    basic_auth=("ssuranie@kargo.com", "KqXtK3YEJCSMtSw1zbSN8456"),  # Jira Cloud: a username/token tuple
)

lstProjects = jira.projects()

dictGoogleServices = getGoogleServices()
if dictGoogleServices["success"] == True:
	
	sheetsService = dictGoogleServices["sheets-service"]

	for thisBoard in lstProjects: 

		lstIssues = getIssues(thisBoard):
		break


