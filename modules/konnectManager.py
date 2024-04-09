#python script to access the interactgo api

import requests
import json
import datetime
import os
import csv
import traceback

#########################
# CONSTANTS
#########################

accessToken = ""
tenantGuid = "5e1a83f8-6f9c-4bbc-af61-d1cccd11e925"
dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
rootURL = "https://us-lb-api-01.interactgo.com/"

def getAPage(pageId):

     print("Getting page " + pageId + "...")

     #use the api token returned in the login call
     dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
     response = requests.get(rootURL + "api/page/" + str(pageId) + "/composer/latest", headers=dictHeader)

     return response.json()


def getAllPages():

     print("Getting all pages...")

     #use the api token returned in the login call
     dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
     response = requests.get(rootURL + "api/search?searchTerm=*&limit=1500&sortBy=DateDesc&Type=Page", headers=dictHeader)
     return response.json()["Results"]

def getSectionTitle(sectionId, strTitle):

     print("Getting page section name...")

     strLocation = "Unknown"

     #use the api token returned in the login call
     dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
     response = requests.get(rootURL + "api/search?searchTerm=" + strTitle + "&limit=1&section=" + str(sectionId) + "& includeChildSections=true", headers=dictHeader)

     if len(response.json()["Results"]) > 0:
        strLocation = response.json()["Results"][0]["Location"]

     return strLocation

#gets the html content of a page
def getPageContent(pageId): 

     print("Getting " + pageId + " page contents...")
     strPageHTML = ""
     dictThisPage = getAPage(pageId)

     #some html is a property of the entity object
     if "Entity" in dictThisPage: 
          strPageHTML = dictThisPage["Entity"]["Html"]

     #some html is a property of the content object
     if "Content" in dictThisPage:
          strPageHTML = dictThisPage["Content"]["Html"]


     return strPageHTML

#gets the assets url path from the html of a page
def getPageAssets(pageId):

     lstAssets = []

     print("Getting " + pageId + " assets...")
     strContent = getPageContent(pageId)
     print("Checking for embeds...")
     lstAssets.extend(getPageElements(strContent, "iframe"))
     print("Checking for links...")
     lstAssets.extend(getPageElements(strContent, "href"))
     print("Checking for imgs...")
     lstAssets.extend(getPageElements(strContent, "img"))
     print(lstAssets)

#returns all requested items from the content
def getPageElements(strContent, strElement):

     lstItems = []

     if strElement == "iframe": 

          lstStrEmbeds = strContent.split("</iframe>")

          for idx, thisEmbed in enumerate(lstStrEmbeds):

               #last item will not be an embed
               if "<iframe" in thisEmbed: 

                    try:
                         strSrc = thisEmbed.split("<iframe")[1].split("src=\"")[1].split("\"")[0]
                         lstItems.append(strSrc)
                    except Exception as e:
                         print("Error with creating page data...")
                         print(e)
                         print(traceback.format_exc())

     elif strElement == "href":

          lstStrHref = strContent.split("</a>")

          for idx, thisLink in enumerate(lstStrHref):

               #last item will not be an embed
               if "href" in thisLink:

                    try:
                         strSrc = thisLink.split("href=\"")[1].split("\"")[0]
                         lstItems.append(strSrc)
                    except Exception as e:
                         print("Error with creating page data...")
                         print(e)
                         print(traceback.format_exc())

     elif strElement == "img":

          lstStrImg = strContent.split("<img")

          for idx, thisImg in enumerate(lstStrImg): 
               
               if "src" in thisImg: 
                    try: 
                         strSrc = thisImg.split("src=\"")[1].split("\"")[0].split("&amp;")[0]
                         lstItems.append(strSrc)
                    except Exception as e:
                         print("Error with creating page data...")
                         print(e)
                         print(traceback.format_exc())

     return lstItems

def getAnAsset(assetId):

     print("Getting asset " + str(assetId) + "...")

     #use the api token returned in the login call
     dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
     response = requests.get(rootURL + "api/asset/" + str(assetId) + "?size=6", headers=dictHeader)

     #need to figure out how to handle this, looks like it is binary data
     print(response.text)


def createAPage(dictPageData):

     #use the api token returned in the login call
     dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
     json_object = json.dumps(dictPageData, indent = 4) 

     response = requests.post(rootURL + "api/page/composer", headers=dictHeader, json=json_object)

     print(response.status_code)

def updateAPage(dictPageData):
     
     jsonPage = json.dumps(dictPageData, indent = 4) 
        
     strURL = rootURL + "api/page/" + pageId + "/composer"
     dictHeader = {"Content-Type": "application/json; charset=utf-8", "accept": "application/json", "X-Tenant":tenantGuid, "Authorization": "Bearer " + accessToken}
     try:
          response = requests.put(strURL, json=jsonPage, headers=dictHeader) # 
          print(response.status_code)
          print(response.json())

     except Exception as e: 
          print("Error with updating page data...")
          print(e)
          print(traceback.format_exc())

   


    

     
    