#this app manages all the api calls for Confluence and returns the data from those calls

#module import
import requests


class ConfluenceManager: 

	#set up headers for confluence access for both stitcher and kargo

	strCommerceAuth = 'Basic c3N1cmFuaWVAa2FyZ28uY29tOkFUQVRUM3hGZkdGMDhfNVJKNlhfUzd2dmlhVmxwd0wyMU5xRmg2SHB0NEZJZjZWaXBONEN0M0VocXJoYW9raEJObDJTOE5Lamo5NWtuZzNuNG8yamtBNlhnVzNDM3RXWThjRERrM0htc1BMS2s2REFNaWJaS1A4VjZjdjlETG9jZWN3TEoyVFpyOEhraGRrM2oyal9TQWRhVmRDS1A1VnBxNHZQR2ZkbDhueFFFOXpYcVM4T2NtTT0zQUQyNTRCNQ=='

	strKargoAuth = 'Basic a3RjQGthcmdvLmNvbTpldVFvbXhwd3RtaGpBUUh1UW10VDVBNjQ='

	#methods

	def callAPI(self, strQuery, sourceType): 

		#get correct auth
		strAuth = ""
		if sourceType == 0:
			strAuth = self.strKargoAuth
		elif sourceType == 1: 
			strAuth = self.strCommerceAuth

		strConfHeaders = {'Authorization': strAuth, 'Content-Type': 'application/json'}

		response = requests.get(strQuery, headers=strConfHeaders)

		if response.status_code == 200:
			return {"success":True, "data":response.json()}
		elif response.status_code > 200:
			return {"success":False, "msg":"There was an error with your requests: \n\n" + "Status Code: " + str(response.status_code) + "\nURL: " + strURL}

	def getPageContent(self, pageId):

		strAuth = self.strKargoAuth
		strURL = (f'https://kargo1.atlassian.net/wiki/rest/api/content/{pageId}?expand=body.export_view')
		
		strConfHeaders = {'Authorization': strAuth, 'Content-Type': 'application/json'}

		response = requests.get(strURL, headers=strConfHeaders)

		if response.status_code == 200:
			return {"success":True, "data":response.json()}
		elif response.status_code > 200:
			return {"success":False, "msg":"There was an error with your requests: \n\n" + "Status Code: " + str(response.status_code) + "\nURL: " + strURL}


	def getPageAttachments(self, pageId, sourceType):

		strURL = ""
		cql = f"cql=type = attachment and container = {pageId}"

		if sourceType == 0:
			strURL = (f'https://kargo1.atlassian.net/wiki/rest/api/content/search?{cql}')
		elif sourceType == 1: 
			strURL = (f'https://stitcherads.atlassian.net/wiki/rest/api/content/search?{cql}')

		try: 
			response = self.callAPI(strURL, sourceType)
			print(response)
		except: 
			print("Could not make request.")

	def getGroups(self):

		strAuth = self.strKargoAuth
		strURL = (f'https://kargo1.atlassian.net/wiki/rest/api/group/')

		strConfHeaders = {'Authorization': strAuth, 'Content-Type': 'application/json'}

		response = requests.get(strURL, headers=strConfHeaders)

		if response.status_code == 200:
			return {"success":True, "data":response.json()}
		elif response.status_code > 200:
			return {"success":False, "msg":"There was an error with your requests: \n\n" + "Status Code: " + str(response.status_code) + "\nURL: " + strURL}

	def getGroupMembers(self, strGrpName):
		#group/member?name={name}
		strAuth = self.strKargoAuth
		strURL = (f'https://kargo1.atlassian.net/wiki/rest/api/group/member?name={strGrpName}')

		strConfHeaders = {'Authorization': strAuth, 'Content-Type': 'application/json'}

		response = requests.get(strURL, headers=strConfHeaders)

		if response.status_code == 200:
			return {"success":True, "data":response.json()}
		elif response.status_code > 200:
			return {"success":False, "msg":"There was an error with your requests: \n\n" + "Status Code: " + str(response.status_code) + "\nURL: " + strURL}



		

		
