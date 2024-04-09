#this app runs jira filters and collates the data into a csv file
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
import os
import datetime
import json
import importlib

colors = importlib.import_module("modules.colors")
appManager = importlib.import_module('modules.appManager')
googleManager = importlib.import_module('modules.googleManager')

am = appManager.AppManager()
cm = colors.ColorManager()
gm = googleManager.GoogleManager()

#this function call the jira api and parses the results
def configJQL(thisBoard):

    #config
    dictResults = {}
    strJQL = ""

    #set date ranges
    dtOneYearPast = datetime.datetime.now() - datetime.timedelta(days=3*365)
    dtThreeWeeksPast = datetime.datetime.now() - datetime.timedelta(days=21)

    #convert to strings
    strOneYearPast = am.formatDateString(dtOneYearPast)
    strThreeWeeksPast = am.formatDateString(dtThreeWeeksPast)

    #sets a jql for each board
    if thisBoard == "KME":
    	strJQL = "project=KME AND status = 'Code Review' OR status = 'IN QA - DEV' OR status = 'IN QA - STG' AND  createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast
    elif thisBoard == "DEAL":
    	strJQL = "project = DEAL AND status = 'IN REVIEW' OR status = 'READY FOR QA' OR status = 'IN QA' AND  createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast
    elif thisBoard == "KAT":
    	strJQL = "project = KAT AND status = 'CODE REVIEW' OR status = 'UAT' OR status = 'QA' OR status = 'In QA' AND  createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast
    elif thisBoard == "KVID":
        strJQL = "project = KVID AND status = 'CODE REVIEW' OR status = 'QA' OR status = 'IN REVIEW' OR status = 'READY FOR QA' OR status = 'ON HOLD/NEED MORE INFO' AND createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast
    elif thisBoard == "CM":
        strJQL = "project = CM AND status = 'IN REVIEW' OR status = 'IN QA' OR status = 'READY FOR QA' OR status = 'READY TO MERGE' AND createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast
    elif thisBoard == "CTV":
        strJQL = "project = CTV AND status = 'CODE REVIEW' OR status = 'IN QA' OR status = 'ON HOLD/NEED MORE INFO' AND createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast
    elif thisBoard == "KRKPD":
        strJQL = "project = KRKPD AND status = 'CODE REVIEW' OR status = 'READY FOR QA' OR status = 'IN QA' OR status = 'ON HOLD/NEED MORE INFO' AND createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast
    elif thisBoard == "KDW":
        strJQL = "project = KDW AND status = 'CODE REVIEW' OR status = 'IN QA' OR status = 'ON HOLD/NEED MORE INFO' AND createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast
    elif thisBoard == "WEB":
        strJQL = "project = KDW AND status = 'CODE REVIEW' OR status = 'IN FEATURE BRANCH' OR status = 'ON HOLD/NEED MORE INFO' OR status = 'IN QA' AND createdDate > " + strOneYearPast + " AND createdDate < " + strThreeWeeksPast

    return strJQL

def queryJQL(jira, strJQL, strBoard):

    try: 
    
        #jira api call - note we need to expand the changelog to return it
        lstIssues = jira.search_issues(strJQL, maxResults=250, expand='changelog')

        if len(lstIssues) > 0: 
            return {"success":True, "issues":lstIssues}
        else:
            return {"success":False, "msg":f"No issues were returned for {thisBoard}"}

    except: 
            return {"success":False, "msg":f"There was an error getting data from {thisBoard}"}



#this function gets the history of the ticket, checks if the entry is for a status change and then checks if the date of the status change is > than 3 weeks ago. 
def checkIfStale(jira, thisIssue):

    isStale = False
    staleDays = 0

    dtCreated = datetime.datetime.strptime(thisIssue.fields.created, '%Y-%m-%dT%H:%M:%S.%f%z')
    daysDelta = am.getDaysSinceDate(datetime.datetime.today(), dtCreated)
    if daysDelta.days > 45: 
        isStale = True
        staleDays = daysDelta.days

    return ({"isStale":isStale, "staleDays":staleDays})

def getLastComment(thisIssue):
    
    strLastComment = ""
    strLastCommentAuthor = ""
    strLastChange = ""
    strLastChangeAuthor = ""

    #get last comment
    if len(thisIssue.fields.comment.comments) > 0:
        
        strLastComment = thisIssue.fields.comment.comments[-1].body
        strLastCommentAuthor = thisIssue.fields.comment.comments[-1].author.displayName
    
    if len(thisIssue.changelog.histories) > 0: 
            strLastChange = thisIssue.changelog.histories[-1].items[-1].toString
            strLastChangeAuthor = thisIssue.changelog.histories[-1].author.displayName

    return {"lastComment":strLastComment, "lastCommentAuthor": strLastCommentAuthor, "lastChange":strLastChange, "lastChangeAuthor":strLastChangeAuthor}    


#this function creates the staleness CSV
def makeCSVFile(dictRows): 

    strCSV = "Key; Summary; Status; Assignee; Created; Staleness (In Days); Author; Last Change; Author; Link; Update\n"

    for thisRow in dictRows:

        dictData = dictRows[thisRow]
        thisIssue = dictData["issue"]

        print(f"{cm.OKGREEN}Writing data for {thisRow}...{cm.ENDC}")

        strAssignee = "Unknown"
        if thisIssue.fields.assignee != None:
            strAssignee = thisIssue.fields.assignee.displayName

        strLink = "https://konnect.kargo.com/Interact/Pages/Content/Document.aspx?id=" + thisRow
        strLinkCellFormula = "=HYPERLINK(\"" + strLink + "\", \"" + thisRow + "\")"


        strCSV = strCSV + thisRow + "; \"" + thisIssue.fields.summary +  "\"; \"" + thisIssue.fields.status.description + "\"; " + strAssignee + "; " + thisIssue.fields.created + "; " + str(dictData["staleDays"]) +  "; " + dictData["lastCommentAuthor"] +  "; \"" + dictData["lastChange"] + "\"; " + dictData["lastChangeAuthor"] +  "; " + strLinkCellFormula + ";\n"
        

    return strCSV

def writeCSV(strCSV):

    print("Writing CSV file...")
    strFileName = datetime.date.today().strftime("%Y-%m-%d") + "-kargo-stale-report"
    dirPath = os.path.expanduser("~/Desktop/Kargo/Projects/QAStaleness/Data/" + strFileName + ".csv") 

    f = open(dirPath, "w")
    f.write(strCSV)
    f.close()
    print(dirPath)

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

def updateSheet(dictStaleTickets, service):

    today = datetime.datetime.now()
    dtToday = f"{today.year}-{today.month}-{today.day}"

    print(f"{cm.OKGREEN}Creating sheet for {dtToday}...{cm.ENDC}")

    sheetId = gm.dictSheets["qaStale"]["id"]
    lstTickets = [["Key", "Summary", "Status", "Assignee", "Staleness (In Days)", "Last Change", "Author"]]
    strSheetTitle = f"{dtToday}-Kargo-Stale-Report"

    for thisTicket in dictStaleTickets: 
        dictThisTicket = dictStaleTickets[thisTicket]
        thisIssue = dictThisTicket["issue"]
        
        strAssignee = "Unknown"
        if thisIssue.fields.assignee != None:
            strAssignee = thisIssue.fields.assignee.displayName

        strLink = "https://konnect.kargo.com/Interact/Pages/Content/Document.aspx?id=" + thisTicket
        strLinkCellFormula = "=HYPERLINK(\"" + strLink + "\", \"" + thisTicket + "\")"


        lstTickets.append([thisTicket, thisIssue.fields.summary, thisIssue.fields.status.name, strAssignee, str(dictThisTicket["staleDays"]), dictThisTicket["lastChange"], dictThisTicket["lastChangeAuthor"]])

    try:

        #add a new sheet to the spread sheet
        body = {
            "requests":{
                "addSheet":{
                    "properties":{
                        "title":strSheetTitle
                    }
                }
            }
        }
        gm.updateSheet(service, sheetId, body)

        body={
            'majorDimension':'ROWS',
            'values': lstTickets}
        gm.overWriteSheet(service, sheetId, strSheetTitle, body)

        #get sheet id 
        lstSheets = gm.getAllSheet(service, sheetId).get('sheets', '')
        for thisSheet in lstSheets:
            if thisSheet["properties"]["title"] == strSheetTitle:
                return {'spreadSheetId':sheetId, "sheetId":thisSheet["properties"]["sheetId"]}

    except Exception as e:
        print(e)

def sendEmail(service, spreadsheetId, sheetId):

    print(f"{cm.OKGREEN}Sending email...{cm.ENDC}")

    dtToday = f"{datetime.datetime.now().year}-{datetime.datetime.now().month}-{datetime.datetime.now().day}"

    strBody = f"The Jira ticket staleness report for <a href=\"https://docs.google.com/spreadsheets/d/{spreadsheetId}/edit#gid={sheetId}\">{datetime.datetime.now().month}/{datetime.datetime.now().year}</a> is now available.<br><br>Let me know if you have any questions.<br><br>Thanks!<br><br>Steve Suranie | <b>Kargo<b><br>Technical Communications Manager<br>ssuranie@kargo.com<br>610.574.0742"

    strSubject = f"Jira Staleness Report {datetime.datetime.now().month}/{datetime.datetime.now().year}"
    gm.sendEmail(service, {"body":strBody, "to":"ssuranie@kargo.com, puneet@kargo.com, kartal@kargo.com, jeremy@kargo.com, frantz@kargo.com, jaymin@kargo.com, julian@kargo.com, moddo@kargo.com", "subject":strSubject})

##############################################
# app starts here
##############################################


#jira setup
jiraOptions = {'server': "https://kargo1.atlassian.net"}
jira = JIRA(options=jiraOptions,
    basic_auth=("ssuranie@kargo.com", "KqXtK3YEJCSMtSw1zbSN8456"),  # Jira Cloud: a username/token tuple
)

lstBoards = ["KME", "DEAL", "KAT", "KVID", "CM", "CTV", "KRKPD", "KDW", "WEB"] #
dictStaleTickets = {}

#get stale tickets
for thisBoard in lstBoards:
    
    print(f"{cm.OKGREEN}Getting JQL for {thisBoard}...{cm.ENDC}")
    strJQL = configJQL(thisBoard)
    dictResults = queryJQL(jira, strJQL, thisBoard)
    if dictResults['success'] == True:
        lstIssues = (dictResults["issues"])
        for thisIssue in lstIssues:

            if thisBoard in thisIssue.key:

                dictIsStale = checkIfStale(jira, thisIssue)

                if dictIsStale["isStale"] == True: 

                    staleDays = dictIsStale["staleDays"]

                    #see if there is a last comment
                    dictComments = getLastComment(thisIssue)

                    dictStaleTickets[thisIssue.key] = {"staleDays":staleDays, "issue":thisIssue, "lastComment": dictComments["lastComment"], "lastCommentAuthor":dictComments["lastCommentAuthor"], "lastChange":dictComments["lastChange"], "lastChangeAuthor":dictComments["lastChangeAuthor"]}

    else: 
        print(dictResults["msg"])

dictGoogleServices = getGoogleServices()
if dictGoogleServices["success"] == False:
    print(dictGoogleServices["error-message"])
else: 
    gmailService = dictGoogleServices["gmail-service"]
    sheetsService = dictGoogleServices["sheets-service"]
    dictSheetData = updateSheet(dictStaleTickets, sheetsService)
    sendEmail(gmailService, dictSheetData["spreadSheetId"], dictSheetData["sheetId"])



