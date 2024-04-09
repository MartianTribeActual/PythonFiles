#this app get stories and tasks associated with an epic
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
import os
import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
import json
import urllib.parse
import requests
import importlib

colors = importlib.import_module("modules.colors")
appManager = importlib.import_module('modules.appManager')

am = appManager.AppManager()
cm = colors.ColorManager()

rootAPIURL = "https://kargo1.atlassian.net/rest/api/2/search?jql="
rootURL = "https://kargo1.atlassian.net"

##############################################
# functions
##############################################

def getAttachmentsFromIssue(strBoard, jira):

	viewCount = 0
	startAt = -50
	
	lstAttachData = []
	dtEarlier = date.today() + relativedelta(months=-6)

	while startAt < 1001:

		startAt += 50 

		print(f"{cm.OKGREEN}Getting {strBoard} results from {startAt} to {startAt + 50}{cm.ENDC}")

		#search for issues
		lstIssues = jira.search_issues(f"project={strBoard}&created<2021-12-31", maxResults=50, startAt=startAt)

		print(len(lstIssues))
		
		#iterate through the issues - we cannot filter for attachments in the search so we need to do it in the results. : (
		for thisIssue in lstIssues:

			#convert created date string to date object
			dateComponents = thisIssue.fields.created.split("T")[0].split("-")
			dtCreated = datetime.datetime.strptime(f"{dateComponents[0]}-{dateComponents[1]}-{dateComponents[2]}", "%Y-%m-%d")

			#check the attachment list for content 
			if len(thisIssue.fields.attachment) > 0: 

				pngCount = 0
				jpgCount = 0
				movCount = 0
				m4pCount = 0
				mpgCount = 0
				unknownFormatCount = 0
				totalVidSize = 0
				totalImgSize = 0

				for thisAttach in thisIssue.fields.attachment:

					try:
						#get file size
						#file_size = os.path.getsize(thisAttach.content)
						fileSizeInBytes = requests.get(thisAttach.content, auth=("ssuranie@kargo.com", "KqXtK3YEJCSMtSw1zbSN8456"), stream=True).headers['Content-length']

						attachExt = str(thisAttach).split(".")[-1]
						if attachExt == "png":
							pngCount += 1
							totalImgSize += round(int(fileSizeInBytes)/1000000,2)
						elif attachExt == "jpg":
							jpgCount += 1
							totalImgSize += round(int(fileSizeInBytes)/1000000,2)
						elif attachExt == "mov": 
							movCount += 1
							totalVidSize += round(int(fileSizeInBytes)/1000000,2)
						elif attachExt == "mpg": 
							mpgCount += 1
							totalVidSize += round(int(fileSizeInBytes)/1000000,2)
						elif attachExt == "m4p": 
							m4pCount += 1
							totalVidSize += round(int(fileSizeInBytes)/1000000,2)
						else:
							unknownFormatCount += 1
						
					except FileNotFoundError:
						print(f"File : {thisAttach.content} not found.")
					except OSError:
						print("OS error occurred.")
					except Exception as e: 
						print(f"There was an error getting the file data!\n{e}")

				lstAttachData.append({"key": thisIssue.key, "summary":thisIssue.fields.summary, "count":len(thisIssue.fields.attachment), "png": pngCount, "jpg":jpgCount, "mov": movCount, "mpg": mpgCount, "m4p":m4pCount, "totalImgSize": totalImgSize, "totalVidSize":totalVidSize, "unknown": unknownFormatCount, "created": dtCreated})
			
	return lstAttachData

def composeData(lstData): 

	strCSV = "Issue; Summary; Created; Attachments; Total Image Size; Total Video Size\n"
	totalVideoSize = 0
	totalImageSize = 0

	for thisIssue in lstData: 

		strLink = "https://kargo1.atlassian.net/browse/" + thisIssue["key"]
		strLinkCellFormula = "=HYPERLINK(\"" + strLink + "\", \"" + thisIssue["key"] + "\")"

		strCSV += f'{strLinkCellFormula}; {thisIssue["summary"]}; {thisIssue["created"]}; {thisIssue["count"]}; {thisIssue["totalImgSize"]}; {thisIssue["totalVidSize"]}\n'
		totalVideoSize += int(thisIssue['totalVidSize'])
		totalImageSize += int(thisIssue["totalImgSize"])

	return {"csv": strCSV, "count": len(lstData), "sizes": {"video": totalVideoSize, "image": totalImageSize}}

##############################################
# app starts here
##############################################

#jira setup
print(f"{cm.OKGREEN}Getting Jira authentication JQL...{cm.ENDC}")
jiraOptions = {'server': "https://kargo1.atlassian.net"}
jira = JIRA(options=jiraOptions,
    basic_auth=("ssuranie@kargo.com", "KqXtK3YEJCSMtSw1zbSN8456"),  # Jira Cloud: a username/token tuple
)

lstResults = getAttachmentsFromIssue("KME", jira)
dictResults = composeData(lstResults)

strFileName = datetime.date.today().strftime("%Y-%m-%d") + "-KME-volume"
dirPath = os.path.expanduser("~/Desktop/Kargo/Projects/Jira/Data/VolumeCheck/" + strFileName + ".csv")
try:
	am.writeFile(dirPath, dictResults["csv"])
except Exception as e:
	print(e)

print(f"Number of Records: {dictResults['count']}\nTotal Video Size: {int(dictResults['sizes']['video'])*0.001}GB\nTotal Image Size: {dictResults['sizes']['image']}MB")
	
