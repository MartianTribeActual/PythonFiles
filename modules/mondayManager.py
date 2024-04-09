#this is the monday api manager

### Note on the queries - these are graphQL queries. Basically passing JSON like structures for the query. The double {{ }} are only for Python, it is how you escape the single {} in the string formats. To see the clean graphQL which you can use in the Monday.com dev section view the 

###

import requests
import json
from enum import Enum
import importlib

# import modules from relative paths
colors = importlib.import_module('modules.colors')
cm = colors.ColorManager()

class itemType(Enum):
	E = "epic"
	D = "default"

class MondayManager:

	dictBoards = {"product-lines":"4023074162", "themes":"4023102011", "projects":"4035946526", "engineering-points":"4036050693"}
	dictThemeCols = {"status":"mirror2", "OKRs":"connect_boards3", "priority": "priority", "product-line":"board_relation", "projects":"link_to_projects"}
	dictProjectCols = {"themes":"connect_boards", "product-line": "mirror", "points": "formula", "epics":"files", "description": "long_text", "eng-pts":"numbers", "fe-eng-pts":"dup__of_ux__pts_", "be-eng-pts":"dup__of_fe_eng", "data-eng-pts":"numbers0", "ds-eng-pts": "numbers1", "ux-pts":"numbers3"}

	def __init__(self, mondayToken):
		self.mondayToken = mondayToken

	def getAllGroups(self, boardId, mondayToken): 

		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken, 'API-Version' : '2024-01'}
		mondayURL = "https://api.monday.com/v2"
		try: 

			query = f'{{boards (ids: {boardId}) {{ groups {{ title id }} }} }}'
			data = {'query' : query}

			r = requests.post(url=mondayURL, json=data, headers=dictHeader) 
			return r.json()["data"]

		except Exception as e: 
			print (f"{cm.WARNING}There was an error getting all the groups from the board: {boardId}\n{e}")

	def getAllGroupItems(self, boardId, groupId, mondayToken):

		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken, 'API-Version' : '2024-01'}
		mondayURL = "https://api.monday.com/v2"

		try: 
			query = f'{{boards (ids: {boardId}) {{ groups (ids:["new_group"]) {{ title id items_page (limit:500) {{ items {{ name id column_values{{ column {{title}} id text value }} }} }} }} }} }}'
    
			data = {'query' : query}

			r = requests.post(url=mondayURL, json=data, headers=dictHeader)
			return r.json()["data"]

		except Exception as e: 
			print (f"{cm.WARNING}There was an error getting all the groups items from the group: {groupId}\nQuery: {query}\n{e}")

	def getItemIdByColValue(self, boardId, colId, colValue):

		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken, 'API-Version' : '2024-01'}
		mondayURL = "https://api.monday.com/v2"
		try:
			
			query = f'{{items_page_by_column_values (limit: 50, board_id: {boardId}, columns: [{{column_id: "{colId}", column_values: ["{colValue}"]}}]) {{ cursor items {{ id name }} }} }}'
    
			data = {'query' : query}

			r = requests.post(url=mondayURL, json=data, headers=dictHeader) 
			return r.json()["data"]

		except Exception as e: 
			print (f"{cm.WARNING}There was an error getting the item id for board id: {boardId} and column id: {colValue}\nQuery: {query}\n{e}") 


	def getGroupItemsAndColumns(self, boardId, groupId, mondayToken):

		try:

			dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken}
			mondayURL = "https://api.monday.com/v2"
			#query = f'{{boards (ids: {boardId}) {{ groups(ids:[{groupId}]) {{ title id items {{ name column_values {{ id text }} }} }} }} }}'
			#query = f'{{boards (ids: {boardId}) {{ groups(ids:[{groupId}]) {{ title id items_page {{ items {{ name column_values {{ id text }} }} }} }} }} }}'
			print(type(groupId))
			query = f'{{boards (ids: {boardId}) {{ groups (ids:{str(groupId)}) {{ title id }} }} }}'
			data = {'query' : query}

			r = requests.post(url=mondayURL, json=data, headers=dictHeader) 

			print(r.json())
			return r.json()["data"]

		except Exception as e: 
			print(f"{cm.WARNING}There was an error getting the group items and columns!\n{e}{cm.ENDC}")

	def createItem(self, boardId, itemName, dictData, itemType, mondayToken):

		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken, 'API-Version' : '2024-01'}
		mondayURL = "https://api.monday.com/v2"
		try:

			query = "mutation ($boardId: ID!, $myItemName: String!, $columnVals: JSON!) { create_item (board_id:$boardId, item_name:$myItemName, column_values:$columnVals) { id } }"
			myVars = {
				"boardId": boardId,
				"myItemName": itemName,
				"columnVals": json.dumps({
					"numbers9":"0",
					"numbers7":"0",
					"numbers72":"0",
					"numbers92":"0",
					"text8":dictData["epic"]
				})
			}

			data = {'query': query, 'variables': myVars}
			r = requests.post(url=mondayURL, json=data, headers=dictHeader) 

			print(r.json())

		except Exception as e: 
			print (f"{cm.WARNING}There was an error creating a new item:\n{e}")

	def upDateItem(self, data, mondayToken):

		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken, 'API-Version' : '2024-01'}
		mondayURL = "https://api.monday.com/v2"

		boardId = data["boardId"]
		itemId = data["itemId"]
		columns = data["columnVals"]

		try:

			query = "mutation ($boardId: ID!, $itemId: ID!, $columnVals: JSON!) { change_multiple_column_values(board_id:$boardId, item_id:$itemId, column_values:$columnVals) { id } }"
			myVars = {
				"boardId": boardId,
				"itemId": itemId,
				"columnVals": columns
			}

			data = {'query': query, 'variables': myVars}
			r = requests.post(url=mondayURL, json=data, headers=dictHeader) 

			

		except Exception as e: 
			print (f"{cm.WARNING}There was an error updating {itemId}:\n{e}{cm.ENDC}")
			return {"item":itemId, "error":e}

	def runMyQuery(self, query, mondayToken): 

		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken, 'API-Version' : '2024-01'}
		mondayURL = "https://api.monday.com/v2"

		try: 

			data = {'query': query}
			r = requests.post(url=mondayURL, json=data, headers=dictHeader) 
			return r.json()["data"]

		except Exception as e: 
			print(f"{cm.WARNING}There was an error running your request.\n{e}{cm.ENDC}")


	def makeRequest(self, data):

		dictResponse = {}
		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken}
		mondayURL = "https://api.monday.com/v2"

		r = requests.post(url=mondayURL, json=data, headers=dictHeader) 

		if r.status_code == 200:

			lstKeys = r.json().keys()

			if "errors" in lstKeys:
				print(f'{cm.WARNING}{r.json()["errors"]}{cm.ENDC}')
			else: 
				 dictResponse = r.json()["data"]
		else: 
			print(f'{cm.WARNING}{r.json()["errors"]}{cm.ENDC}')

		return dictResponse

	def postData(self, payload):

		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken}
		mondayURL = "https://api.monday.com/v2"

		response = requests.request("POST", mondayURL, headers=dictHeader, data=payload)
		print(response.status_code)
		print(response.reason)

	def getStatuses(lstItems): 

		lstMondayStatuses = []
		for thisItem in lstItems: 
			for thisCol in thisItem["column_values"]:
				if thisCol["title"] == "Projects Statuses":
					lstStatuses = thisCol["text"].split(",")
					for thisStatus in lstStatuses: 
						if thisStatus.strip() not in lstMondayStatuses and thisStatus != '': 
							lstMondayStatuses.append(thisStatus.strip())

		return lstMondayStatuses
	

	#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

	#the queries below are deprecated as Monday has changed their API: 

	def getGroupItemsAndProjects(self, boardId, groupId, mondayToken):

		dictHeader = {'Content-Type': 'application/json', "Authorization":self.mondayToken}
		mondayURL = "https://api.monday.com/v2"
		query = f'{{boards (ids: {boardId}) {{ groups(ids:[{groupId}]) {{ title id items() {{ name column_values (ids: "link_to_projects") {{ id text }} }} }} }} }}'
			
		data = {'query' : query}

		r = requests.post(url=mondayURL, json=data, headers=dictHeader) 
		return r.json()["data"]

	

	def getItemsAndColumnValues(self, boardId, groupId):

		query = f'{{boards (ids: {boardId}) {{ groups (ids: {groupId}) {{ items() {{ id name column_values (ids: ["board_relation", "link_to_projects", "mirror2"]) {{ id title value text }} }} }} }} }}'

		data = {'query' : query}
		return(self.makeRequest(data))

	def getBoardColumns(self, boardId): 

		query = f"{{ boards(ids: {boardId}) {{ columns {{ id title }} }} }}"
		data = {'query' : query}
		return(self.makeRequest(data))


	def getColumnValues(self, boardId, groupId, lstCols): 

		strColsToRetrieve = ""
		for idx, thisCol in enumerate(lstCols): 

			if idx < len(lstCols) - 1: 
				strColsToRetrieve = strColsToRetrieve + thisCol + ", "
			elif idx == len(lstCols) - 1: 
				strColsToRetrieve = strColsToRetrieve + thisCol

		query = f"{{ boards(ids: {boardId}) {{ groups(ids: [{groupId}]) {{ title id items {{ id name column_values (ids:[{strColsToRetrieve}]) {{ id title text }} }} }} }} }}"
		#print(query)
		data = {'query' : query}
		return(self.makeRequest(data))

	def formatColsToRetrieve(self, lstCols): 

		strColsToRetrieve = ""
		for idx, thisCol in enumerate(lstCols): 
			if idx < len(lstCols) - 1: 
				strColsToRetrieve = strColsToRetrieve + thisCol + ", "
			elif idx == len(lstCols) - 1: 
				strColsToRetrieve = strColsToRetrieve + thisCol

		return(strColsToRetrieve)

	# def createNewBoardItem():



	


				

		



	
	

