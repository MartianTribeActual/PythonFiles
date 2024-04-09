from __future__ import print_function
from datetime import date
import os.path
import base64
import time
import sys
from email.mime.text import MIMEText
from requests import HTTPError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


import importlib

colors = importlib.import_module("modules.colors")
cm = colors.ColorManager()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://mail.google.com/', 'https://www.googleapis.com/auth/drive']

class GoogleManager:

    dictSheets = {"deployLog":{"id":"14Rbs89NKT2ZoOedYKQIbQ9N3M7ynYRo2wZ4g09gsyYw", "sheets":["Recent Releases", "Master List"]}, "qaStale":{"id":"1jK03i2UlmsBDM0hz3qZDZTm11OBSeCuoFQcYGQJkDnQ", "sheets":[]}, "scrumOfScrums": {"id":"1525CYQyXXJdF_60YjOVulj5ZTUCeYU6UHusQUo0yovQ", "sheets":["November 6th"]}, "techOpsCap":{"id":"1O8QPkNzgWjHsF-6yklTVvi7BsgbEBnPjS1ujEXIywpA", "sheets":[]}, "privacy-1":{"id":"/1z7Dfi0LTQvSmi4xXYxyPeZUAoyLVx2PS", "sheets":["DATA TEAM FAQS", "KARGO OVERVIEW", "INVENTORY & AUCTION", "BRAND SAFETY", "PRICING", "DATA", "CREATIVE", "MEASUREMENT"]}, "konnect": {"id":"1M7QFNbQkxmIyeAYWOPNkiFeK_sehCa1_TjJ9FjEadek", "sheets":[]}}

    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://mail.google.com/', 'https://www.googleapis.com/auth/drive']


    def getAuth(self):

        try:
        
            creds = None
            errMsg = "There was an error authenticating to Google. The token is not valid."

            # The file token.json stores the user's access and refresh tokens, and is
            # created automatically when the authorization flow completes for the first
            # time.

            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            # If there are no (valid) credentials available, let the user log in.
            if not creds or not creds.valid:
                print(f"{cm.WARNING}No creds or creds are not valid...{cm.ENDC}")
                if creds and creds.expired and creds.refresh_token:
                    print(f"{cm.WARNING}Refreshing token...{cm.ENDC}")
                    creds.refresh(Request())
                else:
                    credsPath = os.path.expanduser("~/Desktop/Kargo/Development/Python/KargoPy/modules/credentials.json") 
                    flow = InstalledAppFlow.from_client_secrets_file(credsPath, SCOPES)
                    creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            #validate auth
            if creds.valid == False:
                return {"success":False, "error-message":errMsg}
            else:
                return {"success":True, "credentials": creds}

        except Exception as e: 
            return {"success":False, "error-message":f"{cm.WARNING}There was an error getting Google authorization\n{e}{cm.ENDC}"}


    def getService(self, creds, serviceType):

        service = None
        bSuccess = True

        try: 

            if serviceType == 0: 
                return {"success": bSuccess, "service":build('gmail', 'v1', credentials=creds)}
            elif serviceType == 1: 
                return {"success": bSuccess, "service":build('sheets', 'v4', credentials=creds)}
            elif serviceType == 2: 
                return {"success": bSuccess, "service":build('drive', 'v3', credentials=creds)}
            

        except Exception as e: 
            bSuccess = False
            strServiceName = "Gmail"
            if serviceType == 1:
                strServiceName = "Google Sheets"
            return {"success":bSuccess, "error-message":f"{cm.WARNING}There was an error getting the {strServiceName} service.\n{e}{cm.ENDC}"}


    ############################
    # GMAIL FUNCTIONS          #
    ############################


    def getLabels(self, service): 

        results = service.users().labels().list(userId='me').execute()
        lstLabels = results.get('labels', [])
        for thisLabel in lstLabels: 
            if thisLabel["name"] == "UNREAD": 
                print(thisLabel)

    #this function gets a list of messages from the users gmail account based on the labels passed in and a search query. One label is required. The search query is optional. If you do not want to conduct a search just pass "none" for its value. 

    #returns a dictionary object. If successful the dictionary will contain a messages key which will have a list of messages as the value.  
    def getMessages(self, service, lstLabels, strSearch):

        if service is not None:

            bSuccess = True

            try:

                if strSearch == "none" or len(strSearch) == 0:
                    dictMessages = service.users().messages().list(userId='me', labelIds=lstLabels).execute()
                else:
                    dictMessages = service.users().messages().list(userId='me', labelIds=lstLabels, q=strSearch).execute()                

                if "messages" not in dictMessages or len(dictMessages) == 0: 
                    bSuccess = False
                    return {"errMsg":"There were no Kraken updates!"}

                if bSuccess == True:
                    return {"messages":dictMessages}

                else:
                    return {"errMsg":"There was an error retrieving the gmail messages."}

            except Exception as e:
                
                return {"errMsg":f"Error: {e}"}
        else: 
            return {"errMsg":f"Error: The service was not valid."}

    def getMessageData(self, service, messageId):

        dictMessage = {} 


        if service is not None:

            try:

                dictData = service.users().messages().get(userId='me', id=messageId).execute()
                dictPayload = dictData["payload"]
                lstHeaders = dictPayload['headers']
                for thisHeader in lstHeaders: 
                    if thisHeader["name"] == "Date": 
                        dictMessage["date"] = f"{thisHeader['value'].split(',')[1].split(str(date.today().year))[0]}{date.today().year}"
                dictMessage["snippet"] = dictData["snippet"]
                return dictMessage 

            except Exception as e:
                print(e)
        else: 
            return {"errMsg":"Error"}

    def sendEmail(self, service, dictMessage): 

        message = MIMEText(dictMessage['body'], 'html')
        message['to'] = dictMessage['to']
        message['subject'] = dictMessage['subject']
        create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

        try:
            message = (service.users().messages().send(userId="me", body=create_message).execute())
            print(F'{cm.WARNING}sent message to {message} Message Id: {message["id"]}{cm.ENDC}')
        except HTTPError as error:
            print(F'An error occurred: {error}')
            message = None

    ############################
    # SHEETS FUNCTIONS         #
    ############################

    def getSpreadsheet(self, service, spreadSheetId, strRange):

        bSuccess = True
        errMsg = ""

        try:
            sheet = service.spreadsheets()
            values =  sheet.values().get(spreadsheetId=spreadSheetId, range=strRange).execute()
        except Exception as e:
            bSuccess = False
            errMsg = f"{cm.WARNING}There was an issues get spread sheet: {spreadsheetId}\n{e}{cm.ENDC}"

        return {"success":bSuccess, "error-message": errMsg, "values":values}

    def getAllSheet(self, service, spreadSheetId): 

        return service.spreadsheets().get(spreadsheetId=spreadSheetId).execute()

    #add overview
    def overWriteSheet(self, service, spreadSheetId, strRange, myData): 

        try: 
            sheet = service.spreadsheets()
            result = service.spreadsheets().values().update(spreadsheetId=spreadSheetId, range=strRange, valueInputOption='RAW', body=myData).execute()
        except Exception as e: 
            print(e)

    def appendSheet(self, service, spreadSheetId, strRange, myData):

        try: 
            sheet = service.spreadsheets()
            result = service.spreadsheets().values().append(spreadsheetId=spreadSheetId, range=strRange, valueInputOption='RAW', body=myData).execute()
        except Exception as e: 
            print(e)

    def updateSheet(self, service, spreadSheetId, myData):
        try: 
            service.spreadsheets().batchUpdate(spreadsheetId=spreadSheetId, body=myData).execute()
        except Exception as e:
            print(e)


    def clearSheet(self, service, spreadSheetId, strRange): 

        try: 
            sheet = service.spreadsheets()
            sheet.values().clear(spreadsheetId=spreadSheetId, range=strRange).execute()
        except Exception as e: 
            print(e)

    ############################
    # DRIVE FUNCTIONS         #
    ############################

    def createFolderInGDrive(self, driveService, folderName, parentId, driveId):

        try:

            #set up folder hierarchy
            folderMetadata = {
                'name': folderName,
                "parents": [parentId],
                'mimeType': 'application/vnd.google-apps.folder'
            }

            myFolder = driveService.files().create(body=folderMetadata, supportsAllDrives=True).execute()
            return myFolder

        except Exception as e: 

            print(f"{cm.WARNING}There was an error creating the {folderName} folder on GDrive\n{e}{cm.ENDC}")


    def uploadFileToGDrive(self, driveService, filename, filepath, mimetype, parentFolderId): 

        try: 

            #upload file to drive
            fileMetaData = {
                'name': filename, 
                'mimeType': mimetype, 
                'parents': [parentFolderId]
            }

            media = MediaFileUpload(filepath, mimetype=mimetype)

            results = driveService.files().create(body=fileMetaData, media_body=media, fields='id, driveId, owners, originalFilename', supportsAllDrives=True).execute()
            print(results)

            #edit permissions of file
            permResults = driveService.permissions().create(fileId=fileId, supportsAllDrives=True, body={"role": "reader", "type": "anyone"}).execute()

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"{cm.WARNING}There was an error uploading the file {filepath} to GDrive\n{e}\nLine Number: {exc_tb.tb_lineno}{cm.ENDC}")


    def checkIfFileExists(self, driveService, fileId, mimetype, driveId):

        try: 

            bSuccess = False

            response = driveService.files().list(pageSize=1000, fields="files(id, name)", includeItemsFromAllDrives=True, supportsAllDrives=True, corpora="drive", driveId=driveId).execute()
            lstFiles = response.get('files', [])

            myMatchedFile = None
            
            #see if our file id is in the list
            for thisItem in lstFiles: 

                print(f"{cm.OKCYAN}{fileId}:::{cm.OKGREEN}{thisItem['id']}{cm.ENDC}")
                if fileId == thisItem["id"]:
                    bSuccess = True
                    myMatchedFile = thisItem
                    break

            return {"success": bSuccess, "file":myMatchedFile} 

        except Exception as e: 
            print(f'{cm.WARNING}There was an issue getting the file list from the drive {driveId}\n{e}{cm.ENDC}')


    def checkIfFolderExistsByName(self, driveService, strFolderName, driveId):

        bFoundFolder = False

        response = driveService.files().list(
            q="name = '"+ strFolderName +"' and mimeType = 'application/vnd.google-apps.folder'",
            pageSize=1000,
            corpora='user',
            fields = 'files(id, name)',
            includeItemsFromAllDrives=False,
            supportsAllDrives=False
        ).execute()

        lstFolders = response.get('files', [])
        folderId = None
        if len(lstFolders) > 0: 
            for thisFolder in lstFolders: 
                if thisFolder["name"] == strFolderName: 
                    bFoundFolder = True
                    folderId = thisFolder["id"]

        return {"success": bFoundFolder, "id": folderId}

        




        





