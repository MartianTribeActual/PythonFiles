#this is the jira manager
import requests
import json

import importlib

# import modules from relative paths
colors = importlib.import_module('modules.colors')

#for testing
rootURL = "https://kargo1.atlassian.net/rest/api/2"

cm = colors.ColorManager()

class JiraManager:

	#header info
	strAuth = 'Basic a3RjQGthcmdvLmNvbTpldVFvbXhwd3RtaGpBUUh1UW10VDVBNjQ='

	
	#methods

	def jiraConfig(): 
		#jira setup
		print(f"{cm.OKGREEN}Getting Jira authentication JQL...{cm.ENDC}")
		jiraOptions = {'server': "https://kargo1.atlassian.net"}
		jira = JIRA(options=jiraOptions, basic_auth=("ssuranie@kargo.com", "KqXtK3YEJCSMtSw1zbSN8456"))
		return jira

	def getProject(self, strProject):

		strQuery = f"{rootURL}issue/SE-12222/"

		strJiraHeaders = {'Authorization': self.strAuth, 'Content-Type': 'application/json'}
		response = requests.get(strQuery, headers=strJiraHeaders)
		if response.status_code == 200:
			print(response.json())
			#return {"success":True, "data":response.json()}
		elif response.status_code > 200:
			print("There was an error with your requests: \n\n" + "Status Code: " + str(response.status_code) + "\nURL: " + strQuery)
			#return {"success":False, "msg":"There was an error with your requests: \n\n" + "Status Code: " + str(response.status_code) + "\nURL: " + strURL}
		
			
