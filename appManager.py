# this module contains basic functions for working in Python
import os
import datetime
import csv
import collections
from dateutil.relativedelta import relativedelta
from datetime import date, timedelta
import random
import importlib

# import modules from relative paths
colors = importlib.import_module('modules.colors')
cm = colors.ColorManager()

class AppManager: 

	###############################
	# File Management			  #
	###############################

	def readFile(self, strFilePath): 

		# Open a file: file
		file = open(strFilePath,mode='r')
		 
		# read all lines at once
		strFileContents = file.read()
		 
		# close the file
		file.close()

		return strFileContents

	def readBinary(self, strFilePath):
		
		with open(strFilePath, 'rb') as file:
			strFileContents = file.read()

			# close the file
			file.close()

			return strFileContents

	def doesItemExist(self, strFilePath, intType): 

		bExists = False

		if intType == 0:
			if os.path.isfile(strFilePath): 
				bExists = True
		elif intType == 1: 
			if os.path.isdir(strFilePath):
				bExists = True

		return bExists

	def writeFile(self, strFilePath, strFileText):

		
		print(f"{cm.OKGREEN}Writing {strFilePath}...{cm.ENDC}")

		bExists = self.doesItemExist(strFilePath, 0)

		if bExists == True: 
			file = open(strFilePath, "w")
			n = file.write(strFileText)
			file.close()
		else:
			file = open(strFilePath, "x")
			n = file.write(strFileText)
			file.close()

	def readCSVFile(self, strFilePath, displayMessage):

		lstRows = []

		if displayMessage == True:
			print(f"{cm.OKGREEN}Reading {strFilePath}...{cm.ENDC}")

		bExists = self.doesItemExist(strFilePath, 0)

		if bExists == True:
			with open(strFilePath, newline='\n') as csvfile:
				lineReader = csv.reader(csvfile, delimiter=',', quotechar='\"')
				for row in lineReader:
					lstRows.append(row)

		return lstRows


	###############################
	# Date Management			  #
	###############################

	def getDateFreshness(self, daysFresh, strToCheck):

		bIsRedline = false

		dtNewDate = datetime.datetime.strptime(strToCheck.split("T")[0], '%Y-%m-%d')
		dtNow = datetime.datetime.today().strftime('%Y-%m-%d')
		
		dtRedline = dtNow - datetime.timedelta(days = daysFresh)
		if dtNewDate < dtRedline: 
			bIsRedline = true


		return bIsRedline

	def dateIsBetweenDates(self, dtToCheck, dtStart, dtEnd): 

		bIsValid = False

		try: 
			if dtToCheck > dtStart and dtToCheck < dtEnd:
				bIsValid = True
		except Exception as e: 
			print(f"{cm.WARNING}{e}{cm.ENDC}")

		return bIsValid
			

	def getDaysSinceDate(self, dtEnd, dtStart ):

		d0 = datetime.date(dtEnd.year, dtEnd.month, dtEnd.day)
		d1 = datetime.date(dtStart.year, dtStart.month, dtStart.day)
		return d0 - d1

	def stripDate(self, strToStrip):

		dtNewDate = datetime.datetime.strptime(strToStrip.split("T")[0], '%Y-%m-%d')
		return dtNewDate

	#this function formats a date for jira queries
	def formatDateString(self, dtToFormat): 

		#yyyy-MM-dd
		month = dtToFormat.strftime('%m')
		day = dtToFormat.strftime('%d')
		year = dtToFormat.strftime('%Y')

		return year + "-" + month + "-" + day

	def stripDateString(strToStrip):

		lstComponents = strToStrip.split(":")[0].split("T")[0].split("-")
		return lstComponents[1] + "/" + lstComponents[2] + "/" + lstComponents[0]

	def convertMonthNameToInt(self, strMonth):
		
		dictMonths = {}
		dictMonths["January"] = "01"
		dictMonths["Jan"] = "01"
		dictMonths["February"] = "02"
		dictMonths["Feb"] = "02"
		dictMonths["March"] = "03"
		dictMonths["Mar"] = "03"
		dictMonths["April"] = "04"
		dictMonths["Apr"] = "04"
		dictMonths["May"] = "05"
		dictMonths["June"] = "06"
		dictMonths["July"] = "07"
		dictMonths["August"] = "08"
		dictMonths["Aug"] = "08"
		dictMonths["September"] = "09"
		dictMonths["Sept"] = "09"
		dictMonths["Sep"] = "09"
		dictMonths["October"] = "10"
		dictMonths["Oct"] = "10"
		dictMonths["November"] = "11"
		dictMonths["Nov"] = "11"
		dictMonths["December"] = "12"
		dictMonths["Dec"] = "12"

		for thisMonth in dictMonths: 
			if strMonth in thisMonth or strMonth in thisMonth.lower():
				return dictMonths[thisMonth]


	def compareDates(self, dtToCheck):

		bIsOlder = False
		bIsNewer = False
		bIsSame = False

		now = date.today() 
		if now > dtToCheck: 
			bIsOlder = True
		elif now < dtToCheck: 
			bIsNewer = True
		elif now == dtToCheck: 
			bIsSame = True

		return { "older": bIsOlder, "newer": bIsNewer, "same":bIsSame}

	#pass in dates like so: date(YYYY, MM, DD)
	def randomDate(self, dtStart, dtEnd):
    
		lstDays = dtEnd - dtStart
		totalDays = lstDays.days

		random.seed(a=None)
		ranDay = random.randrange(totalDays)

		# getting random date 
		return {"date":dtStart + timedelta(days=ranDay), "day": ranDay}
			


	###############################
	# User Input     			  #
	###############################

	def selectFromList(self, lstOptions, strMsg): 

		usrSelection = ""

		for index, item in enumerate(lstOptions):
			strMsg += f'{cm.WARNING}{index+1}) {item}{cm.ENDC}\n'

		usrSelection = int(input(strMsg))
		return lstOptions[usrSelection-1]

	###############################
	# List Management     	      #
	###############################		
		
	def outputDuplicates(self, lstToCheck): 
		print([item for item, count in collections.Counter(lstToCheck).items() if count > 1])

	###############################
	# Dictionary Management       #
	###############################	

	def is_subdict(self, small, big):
		return big | small == big

	def subDictContainsValue(self, dictMaster, strValueToFind):

		bHasValue = False
		lstKeys = dictMaster.keys()
		
		for thisKey in dictMaster.keys():
			if dictMaster[thisKey] == strValueToFind: 
				bHasValue = True

		return bHasValue

		

