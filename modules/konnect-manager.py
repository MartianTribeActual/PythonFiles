#python script to access the interactgo api

import requests
import json
import datetime
import os
import csv
import lowercase_booleans
import importlib

#import local modules
appManager = importlib.import_module('modules.appManager')
colors = importlib.import_module("modules.colors")

lstDocLeads = [
     {"name": "Steven Suranie", "email": "ssuranie@kargo.com", "comm": "Tech Comms"},
     {"name": "Heather Millington", "email": "heather.millington@kargo.com", "comm": "Performance Management"}, 
     {"name": "Michael Schindler", "email": "mschindler@kargo.com", "comm": "Tech Ops"},
     {"name": "Beck Byler", "email": "becky.byler@kargo.com", "comm": "Client Services"},
     {"name": "Jessica McFadden", "email": "jmcfadden@kargo.com", "comm": "Campaign Management"},
     {"name": "Sarah Galinet", "email": "sgalinat@kargo.com", "comm": "Analytics"},
     {"name": "Michael Schindler", "email": "mschindler@kargo.com", "comm": "DSP Guides"},
     {"name": "Michael Schindler", "email": "mschindler@kargo.com", "comm": "Demand Partnerships"},
     {"name": "Jonathan DeMiceli", "email": "jonathan.dimiceli@kargo.com", "comm": "Product Marketing Team"},
     {"name": "Darlene LaChapelle", "email": "darlene.lachapelle@kargo.com", "comm": "Research"},
     {"name": "Rebecca Buckheit", "email": "rcawley@kargo.com", "comm": "Revenue Operations"}, 
     {"name": "Brittany Spicer", "email": "brittany@kargo.com", "comm": "Ad Design"},
     {"name": "Cydney Robbins", "email": "crobbins@kargo.com", "comm": "Data Partnerships"},
     {"name": "Joe Lanzerotti", "email": "joe.lanzerotti@kargo.com", "comm": "Media Strategy"},
     {"name": "Alexa Simos", "email": "asimos@kargo.com", "comm": "Creative Services"},
     {"name": "Adrienne Ross", "email": "adrienne@kargo.com", "comm": "Retail Media Networks"},
     {"name": "Audrey Bui", "email": "abui@kargo.com", "comm": "Publisher Development"},
     {"name": "Krtstal Cusamanta", "email": "krystle@kargo.com", "comm": "Program Management (PMO)"},
     {"name": "Britney Andersen", "email": "bandersen@kargo.com", "comm": "Agency Partnerships"},
     {"name": "Becca Poetta", "email": "Becca@kargo.com", "comm": "Marketing & Events"},
     {"name": "Billie Hirsch", "email": "billie@kargo.com", "comm": "Marketing"},
     {"name": "Peter Lee", "email": "plee@kargo.com", "comm":"Product Design"}
]

#########################
# CONSTANTS
#########################

am = appManager.AppManager()
cm = colors.ColorManager()

accessToken = ""
tenantGuid = "5e1a83f8-6f9c-4bbc-af61-d1cccd11e925"
dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
rootURL = "https://us-lb-api-01.interactgo.com/"

def getAPage(pageID):

     #use the api token returned in the login call
     dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
     response = requests.get(rootURL + "api/page/" + pageID + "/composer/latest", headers=dictHeader)

     return response.json()

def getAllPages():

    #use the api token returned in the login call
    dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
    response = requests.get(rootURL + "api/search?searchTerm=*&limit=1500&sortBy=DateDesc&Type=Page", headers=dictHeader)

    if response != None: 
          return response.json()["Results"]

def getPageByTitle(strTitle):

     #use the api token returned in the login call
     dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
     response = requests.get(f"{rootURL}api/search?searchTerm='{strTitle}'&limit=1500&sortBy=DateDesc&Type=Page", headers=dictHeader)
     
     for thisData in response.json()["Results"]:
          if thisData["Title"] == strTitle: 
               return thisData

def getPageById(strId):

     #use the api token returned in the login call
    dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
    response = requests.get(f"{rootURL}api/page/{strId}/composer/latest", headers=dictHeader)

    if response != None:
          return response.json()

def createAPage(payload):

     print(f"{cm.OKCYAN}Creating Konnect page...{cm.ENDC}")

     try:

          #this is just for testing, delete when the app is ready
          path = "~/Desktop/Kargo/Development/Python/KargoPy/modules/test.json"
          fullPath = os.path.expanduser(path)
          #testJSON = am.readFile(fullPath)
          
          dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}

          #response = requests.post(rootURL + "/api/page/composer", headers=dictHeader, json=payload)
          response = requests.post(rootURL + "/api/page/composer", data=payload, headers=dictHeader)
          print(str(response.status_code) + ":::" + response.reason)

     except Exception as e:
          print(f"{cm.WARNING}There was an error while trying to create a Konnect page\n{e}{cm.ENDC}") 

def createPageTest(): 

     url = "https://developer.interactgo.com/api/page/composer"

     headers = {"accept": "application/json", "X-Tenant": "5e1a83f8-6f9c-4bbc-af61-d1cccd11e925", "content-type": "application/x-www-form-urlencoded"}

     response = requests.post(url, data=payload, headers=headers)

     print(response.text) 




