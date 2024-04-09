import csv
import os
import traceback
import importlib

# import modules from relative paths
confluenceManager = importlib.import_module('modules.confluenceManager2')
colorsManager = importlib.import_module('modules.colors')
appManager = importlib.import_module('modules.appManager')

#create a cm class
cm = confluenceManager.ConfluenceManager()
am = appManager.AppManager()
clrm = colorsManager.ColorManager

#/rest/api/group/confluence-users/OKTA Confluence

##################
# FUNCTIONS     #
#################

def getUser(strUserName): 

	dictResults = cm.getGroups()
	if dictResults["success"] == True:
		lstGroups = dictResults["data"]["results"]
		for thisGroup in lstGroups: 
			if thisGroup["name"] == "okta confluence":

				#get the okta confluence users
				dictMemberResults = cm.getGroupMembers(thisGroup["name"])
				if dictMemberResults["success"] == True:
					lstUsers = dictMemberResults["data"]["results"]
					for thisUser in lstUsers: 
						if thisUser["displayName"] == strUserName:
							return thisUser
				else:
					print(dictMemberResults["msg"])
				
	else: 
		print(dictResults["msg"])


#######################
# App Starts Here     #
#######################

# get users
dictUser = getUser("Steve Suranie")
strAcctId = dictUser["accountId"]
print(strAcctId)