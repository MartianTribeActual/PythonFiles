#this file is a manager for Confuence. Import it into your main program. 

from atlassian import Confluence
import importlib

# import modules from relative paths
colors = importlib.import_module('modules.colors')


confluence = Confluence(
    url='https://kargo1.atlassian.net',
    username="ktc@kargo.com",   
    password="euQomxpwtmhjAQHuQmtT5A64",
    cloud=True)

commConfluence = Confluence(
    url='https://stitcherads.atlassian.net',
    username="ssuranie@kargo.com",   
    password="ATATT3xFfGF08_5RJ6X_S7vviaVlpwL21NqFh6Hpt4FIf6VipN4Ct3EhqrhaokhBNl2S8NKjj95kng3n4o2jkA6XgW3C3tWY8cDDk3HmsPLKk6DAMibZKP8V6cv9DLocecwLJ2TZr8Hkhdk3j2j_SAdaVdCKP5Vpq4vPGfdl8nxQE9zXqS8OcmM=3AD254B5",
    cloud=True)	



#base64encoded: c3N1cmFuaWVAa2FyZ28uY29tOkFUQVRUM3hGZkdGMDhfNVJKNlhfUzd2dmlhVmxwd0wyMU5xRmg2SHB0NEZJZjZWaXBONEN0M0VocXJoYW9raEJObDJTOE5Lamo5NWtuZzNuNG8yamtBNlhnVzNDM3RXWThjRERrM0htc1BMS2s2REFNaWJaS1A4VjZjdjlETG9jZWN3TEoyVFpyOEhraGRrM2oyal9TQWRhVmRDS1A1VnBxNHZQR2ZkbDhueFFFOXpYcVM4T2NtTT0zQUQyNTRCNQ==


class ConfluenceManager:

	######################

	#this method retrieves either the page content or all page data depending on the request type (0 or 1)

	######################


	def getPageByTitle(self, strTitle, requestType, userType):
		
		dictPage = {}

		if requestType < 0 or requestType > 1: 
			print(f"{colors.WARNING}WARNING!: Request type is invalid. You must indicate if you want just the page content (0) or all data (1)...")
			return dictPage
		else: 
			
			if confluence.page_exists("KTC", strTitle):

				#get the page data
				dictPage = confluence.get_page_by_title("KTC", strTitle, start=0, limit=None, expand="body.storage")

				if len(dictPage) > 0:
					return self.getPageData(dictPage, requestType)
				else:
					print(f"{colors.WARNING}WARNING!: No date was returned for the request of: " + strTitle)
			else: 
				print(f"{colors.WARNING}WARNING!: The page titled: " + strTitle + " could not be retrieved...")

    ######################

	#this method returns page data by passing the page id. You must pass a 0 or 1 to indicate if you only want page content or want all page data (0 = content only, 1 = all data) It will return page content. 

	######################

	def getPageById(self, strId, requestType, userType): 

		dictPage = {}

		if requestType < 0 or requestType > 1: 
			print(f"{colors.WARNING}WARNING!: Request type is invalid. You must indicate if you want just the page content (0) or all data (1)...{colors	.ENDC}")
			return dictPage

		else:

			print(f"{colors.OKGREEN}Calling Confluence for page {strId}...{colors	.ENDC}")

			if userType == 0: 

				dictPage = confluence.get_page_by_id(strId, expand="body.storage", status=None, version=None)

			else: 

				dictPage = commConfluence.get_page_by_id(strId, expand="body.storage", status=None, version=None)

			if len(dictPage) > 0:				
				return self.getPageData(dictPage, requestType)
			else:
				print(f"{colors.WARNING}WARNING!: No date was returned for the request of page: {strId}...{colors	.ENDC}")

			return self.getPageData(dictPage, requestType)

	######################

	#this method filters the page data returned from a request depending on the request type (0 or 1) - see getPageContentByTitle

	######################

	def getPageData(self, dictPage, requestType):

		print(f"{colors.OKGREEN}Filtering data...{colors	.ENDC}")

		dictPageData = {}

		if requestType == 0:
			dictPageData["content"] = dictPage["body"]["storage"]["value"]
		else: 
			dictPageData = dictPage

		return dictPageData
