from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
import requests
import os
from os.path import join
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
import mimetypes
import urllib
import importlib

colors = importlib.import_module("modules.colors")
appManager = importlib.import_module('modules.appManager')
googleManager = importlib.import_module('modules.googleManager')

am = appManager.AppManager()
cm = colors.ColorManager()
gm = googleManager.GoogleManager()

rootAPIURL = "https://kargo1.atlassian.net/rest/api/2/search?jql="
rootURL = "https://kargo1.atlassian.net"

googleDriveParentId = "0AP0O9VQMo9qVUk9PVA"
raFolderId = "13k8oFnqYBtifXizcqSmkMcK0Jl_sh1rt"

##############################################
# functions
##############################################

def getTickets():

	print(f"{cm.OKGREEN}Getting RA Issues...{cm.ENDC}") 

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
		
	

def getIssueData(lstIssues): 

	print(f"{cm.OKCYAN}Getting Issue Data ...{cm.ENDC}") 

	lstMaster = []
	try: 
	
		for thisIssue in lstIssues:

			dictIssue = {}
			dictIssue["key"] = thisIssue.key
			dictIssue["summary"] = thisIssue.fields.summary
			dictIssue["status"] = thisIssue.fields.status
			dictIssue["reporter"] = thisIssue.fields.reporter
			dictIssue["assignee"] = thisIssue.fields.assignee
			dictIssue["description"] = thisIssue.fields.description
			dictIssue["link"] = f"https://kargo1.atlassian.net/browse/{thisIssue.key}"
			dictComments = {}
			dictAttachments = {}

			dictIssue["product"] = "Not Listed"
			if "customfield_14081" in list(dir(thisIssue.fields)):
				dictIssue["product"] = thisIssue.fields.customfield_14081
			
			#get comments
			if len(thisIssue.fields.comment.comments) > 0:
				for idx, thisComment in enumerate(thisIssue.fields.comment.comments):
					strAuthor = thisComment.author.displayName
					strDate = thisComment.created.split('T')[0]
					strTime = thisComment.created.split('.')[0].split("T")[1]
					strTimeStamp = f"{strDate} {strTime}"
					strComment = thisComment.body

					dictComments[idx] = {"author":strAuthor, "timestamp": strTimeStamp, "comment": strComment}

				dictIssue["comments"] = dictComments
			else:

				dictIssue["comments"] = {}

			if len(thisIssue.fields.attachment) > 0:
				for idx, thisAttachment in enumerate(thisIssue.fields.attachment):
					strFilename = thisAttachment.filename
					strAuthor = thisAttachment.author.displayName
					strDate = thisAttachment.created.split('T')[0]
					strTime = thisAttachment.created.split('.')[0].split("T")[1]
					strTimeStamp = f"{strDate} {strTime}"
					strLink = f"{rootURL}/secure/attachment/{thisAttachment.id}/{urllib.parse.quote(thisAttachment.filename)}"
					strJiraFilePath = thisAttachment.content

					dictAttachments[idx] = {"filename":strFilename, "author":strAuthor, "timestamp": strTimeStamp, "link":strLink, "jira-path": strJiraFilePath}

				dictIssue["attachments"] = dictAttachments

			else: 
				dictIssue["attachments"] = {}

			#get attachments
			lstMaster.append(dictIssue)

		return lstMaster

	except Exception as e: 

		print(f"{cm.WARNING}There was an issue with getting the issue data for {thisIssue.key}\n{e}{cm.ENDC}")

def addItemsToGDrive(strBoard, lstItems):

	print(f"{cm.OKCYAN}Adding items to the {strBoard} folder...{cm.ENDC}")

	try: 

		pathToGoogle = os.path.expanduser("Google Drive/My Drive/Jira Backup/")

		for thisItem in lstItems:

			#make sure the folder was created
			if os.path.exists(f"{pathToGoogle}/{strBoard}/{thisItem['key']}") == False:
				os.mkdir(f"{pathToGoogle}/RA/{thisItem['key']}")

			if os.path.exists(f"{pathToGoogle}/{strBoard}/{thisItem['key']}/assets") == False:
				os.mkdir(f"{pathToGoogle}/RA/{thisItem['key']}/assets")

			#add assets
			dictAttachments = thisItem["attachments"]

			if len(dictAttachments) > 0:
				for idx in dictAttachments:
					manageAttachments(dictAttachments[idx], f"{pathToGoogle}/RA/{thisItem['key']}/assets")

			createFileContent(thisItem, f"{pathToGoogle}/RA/{thisItem['key']}/{thisItem['key']}.txt")
			#break

	except Exception as e: 

		print(f"{cm.WARNING}There was an issue adding {thisItem['key']} to Google Drive\n{e}{cm.ENDC}")

def createFileContent(thisItem, pathToWrite):

	print(f"{cm.OKCYAN}Creating file for {thisItem['key']} folder...{cm.ENDC}")

	try: 

		strBody = f"Contents of {thisItem['key']}"
		#create file contents
		strBody += f"{thisItem['summary']}\n"
		strBody += f"Ticket: {thisItem['key']}\n"
		strBody += f"Reporter: {thisItem['reporter']}\n"
		strBody += f"Assignee: {thisItem['assignee']}\n"
		strBody += f"Status: {thisItem['status']}\n"
		strBody += f"Link: {thisItem['link']}\n"
		strBody += f"Description:\n{thisItem['description']}\n"
		strBody += f"Product: {thisItem['product']}\n"
		strBody += "_____________________________________\n"
		strBody += f"\nComments:\n\n"

		if len(thisItem["comments"]) > 0:
			dictComments = thisItem["comments"]
			for idx in dictComments: 
				dictComment = dictComments[idx]
				strBody += f"Author: {dictComment['author']}\n"
				strBody += f"Timestamp: {dictComment['timestamp']}\n"
				strBody += f"Comment: {dictComment['comment']}\n"
				strBody += "_____________________________________\n\n"

		strBody += f"\nAttachments:\n\n"
		if len(thisItem["attachments"]) > 0:
			dictAttachments = thisItem["attachments"]
			for idx in dictAttachments:
				dictAttachment = dictAttachments[idx]
			strBody += f"Filename: {dictAttachment['filename']}\n"
			strBody += f"Author: {dictAttachment['author']}\n"
			strBody += f"Timestamp: {dictAttachment['timestamp']}\n"
			strBody += "_____________________________________\n\n"

		#write file to path as txt file
		am.writeFile(f"{pathToWrite}", strBody)

	except Exception as e: 

		print(f"{cm.WARNING}There was an issue creating the file body text for {thisItem['key']} to Google Drive\n{e}{cm.ENDC}")

def manageAttachments(dictAttachment, pathForFile):

	print(f"{cm.OKCYAN}Adding attachments to the ticket folder...{cm.ENDC}")

	try: 

		#download attachment to desktop
		r = requests.get(dictAttachment["jira-path"], auth=("ssuranie@kargo.com", "(MyNewPassword12)"), stream=True)
		#path = os.path.expanduser("Desktop/holding-cell/")
		storedPath = join(pathForFile, dictAttachment['filename'])
		file = open(storedPath,'w')   
		file.close()

	except Exception as e: 

		print(f"{cm.WARNING}There was an issue downloading the {dictAttachment['filename']} to Google Drive\n{e}{cm.ENDC}")

def checkForDirectory(strName):

	print(f"{cm.OKGREEN}Checking if {strName} folder exists...{cm.ENDC}") 

	bHasFolder = False 

	#get the folders in my drive
	lstFolders = []
	pathToGoogle = os.path.expanduser("Google Drive/My Drive")
	lstItems = os.listdir(pathToGoogle)
	for thisItem in lstItems:
		itemPath = f"{pathToGoogle}/{thisItem}"
		if os.path.isdir(itemPath): 
			lstFolders.append(thisItem)

	#check if the RA folder exists
	if strName not in lstFolders: 
		os.mkdir(f"{pathToGoogle}/{strName}")

	#make sure the folder was created
	if os.path.exists(f"{pathToGoogle}/{strName}") == True:
		bHasFolder = True

	return bHasFolder

def updateGoogleSheet(lstIssues, sheetsService):

	print(f"{cm.OKGREEN}Updating Google Sheet...{cm.ENDC}")

	try:  

		sheetId = "1tBNzMQnYTINeblhTyNzdxs-FH2Tn1PDP2qCjts26J5c"

		sheetData = [["Ticket", "Summary", "Assignee"]]

		for thisIssue in lstIssues:

			strLink = "https://konnect.kargo.com/Interact/Pages/Content/Document.aspx?id=" + thisIssue["key"]
			strLinkCellFormula = "=HYPERLINK(\"" + strLink + "\", \"" + thisIssue["key"] + "\")"

			sheetData.append([strLinkCellFormula, thisIssue["summary"], thisIssue["assignee"]])	

		body={
			'majorDimension':'ROWS',
			'values': sheetData}

		gm.updateSheet(sheetsService, sheetId, body)

	except Exception as e: 

		print(f"{cm.WARNING}There was an error writing the Google sheet\n{e}{cm.ENDC}")


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

	for idx, thisBoard in enumerate(lstProjects):
		if idx == 0: 
			lstIssues = getTickets()
			print(len(lstIssues))
			#lstIssues = getIssueData(dictEpics[strBoard])

	# updateGoogleSheet(lstIssues, sheetsService)





