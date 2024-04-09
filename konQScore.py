import base64
from email.mime.text import MIMEText
import os
from os.path import join
import tkinter as tk
from tkinter import filedialog
from operator import itemgetter
from datetime import datetime, date, timedelta
import importlib

colors = importlib.import_module("modules.colors")
appManager = importlib.import_module('modules.appManager')
konnectManager = importlib.import_module('modules.konnect-manager')
konnectLogin = importlib.import_module('modules.konnect-login')
googleManager = importlib.import_module('modules.googleManager')

#build managers
cm = colors.ColorManager()
am = appManager.AppManager()
kl = konnectLogin.KonnectLogin("ssuranie@kargo.com", "(AnimalHouse12)")
gm = googleManager.GoogleManager()



#---------------FUNCTIONS----------------------

def setUpCommunities():

	try: 

		dictCommunities = {}
		lstDocLeads = konnectManager.lstDocLeads

		for thisDocLead in lstDocLeads:
			dictThisCommunity = {}
			dictThisCommunity["docLead"] = thisDocLead["name"]
			dictThisCommunity["docLeadEmail"] = thisDocLead["email"]
			dictThisCommunity["pages"] = []
			dictCommunities[thisDocLead["comm"]] = dictThisCommunity

		return dictCommunities

	except Exception as e: 
		print(f"{cm.WARNING}There was an issue setting up the communities\n{e}{cm.ENDC}")

def getUniquePageViews(lstPages, csvFilePath, dictCommunities):

	print(f"{cm.OKGREEN}Getting page metadata...{cm.ENDC}")

	
	try:
		#read the csv file
		lstRows = am.readCSVFile(os.path.expanduser(csvFilePath), False)

		for thisPage in lstPages: 

			dictPageMeta = {}
			dictPageMeta["title"] = thisPage["Title"]
			dictPageMeta["pubDate"] = thisPage["DateUpdated"]
			dictPageMeta["author"] = thisPage["Author"]
			dictPageMeta["community"] = thisPage["Location"]
			dictPageMeta["comments"] = thisPage["NoOfComments"]
			dictPageMeta["likes"] = thisPage["NoOfLikes"]

			for idx, thisRow in enumerate(lstRows):
				if thisRow[0] ==  dictPageMeta["title"]:
					dictPageMeta["views"] = thisRow[7]
				break

			break

	except Exception as e: 
		print(f"{cm.WARNING}There was an issue setting page metadata\n{e}{cm.ENDC}")

#---------------APP START----------------------

if __name__ == '__main__':


	#retrieves the access token so we can be authenticated for additional calls. 
	print(f"{cm.OKCYAN}Logging into Interact API...{cm.ENDC}")
	dictAccess = kl.login()

	if "access_token" in dictAccess:  
		print(f"{cm.OKGREEN}Access token retrieved...{cm.ENDC}")
		konnectManager.accessToken = dictAccess["access_token"]
		lstPageMeta = []

		print(f"{cm.OKCYAN}Select CSV file...{cm.ENDC}")
		#csvFilePath = filedialog.askopenfilename()
		csvFilePath = os.path.expanduser("Desktop/Kargo/Projects/Intranet/Data/Analytics/2024-02-22.csv")

		print(f"{cm.OKCYAN}setting up communities...{cm.ENDC}")
		dictCommunities = setUpCommunities()

		#get all Konnect pages
		print(f"{cm.OKGREEN}Getting Konnect pages...{cm.ENDC}")
		lstPages = konnectManager.getAllPages()

		getUniquePageViews(lstPages, csvFilePath, dictCommunities)



