import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
from matplotlib.pyplot import axis
import base64
from email.mime.text import MIMEText
from io import BytesIO
import xml.etree.ElementTree as ET
import sys
import shutil
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

strCSVPath = os.path.expanduser("Desktop/Kargo/Projects/Intranet/Data/Analytics/02-05-2023-view.csv")
strRootPath = os.path.expanduser("Desktop/Kargo/Projects/Intranet/Data/Analytics/Matrix/")

driveId = "0AP0O9VQMo9qVUk9PVA"

lstDocLeads = konnectManager.lstDocLeads


#---------------FUNCTIONS----------------------

def getUniquePageViews(lstPages, csvFilePath):

	print(f"{cm.OKGREEN}Getting page views...{cm.ENDC}")

	lstPagesData = []
	matplotct = 0
	try:
		#read the csv file
		lstRows = am.readCSVFile(os.path.expanduser(csvFilePath), False)

		#loop through the returned page data
		for thisPage in lstPages: 

			#set some configs - matplotct is an identifier for each page
			views = -1
			matplotct += 1

			#meta data
			strTitle = thisPage["Title"]
			strId = thisPage["Id"]
			dtCreated = datetime.strptime(thisPage["DateAdded"].split("T")[0], "%Y-%m-%d")
			dtUpdated = datetime.strptime(thisPage["DateUpdated"].split("T")[0], "%Y-%m-%d")
			today = datetime.now()
			dtToday = datetime.strptime(str(f"{today.year}-{today.month}-{today.day}"), "%Y-%m-%d")
			intDaysOld = am.getDaysSinceDate(dtToday, dtUpdated).days
			strCommunity = thisPage["Location"]
			
			for thisRow in lstRows:
				if len(thisRow) > 0 and strTitle in thisRow:
					views = thisRow[7]

			lstPagesData.append({"title":strTitle, "created": dtCreated, "updated": dtUpdated, "views": int(views), "ripeness": intDaysOld, "plotNum": matplotct, "url": f"https://konnect.kargo.com/page/{thisPage['Id']}", "community":strCommunity})

		
	except Exception as e: 
		print(f"{cm.WARNING}{e}{cm.ENDC}")

	return sorted(lstPagesData, key=itemgetter('views'))

def getCommunityPages(lstPages, thisCommunity): 

	lstCommPages = []

	for thisPage in lstPages: 
		if thisPage["community"] == thisCommunity: 
			lstCommPages.append(thisPage)

	return lstCommPages
	
def plotCoords(dictCommPages):

	#set up data
	for thisCommunity in dictCommPages:

		print(f"\n{cm.OKCYAN}Plotting page coordinates for {thisCommunity}...{cm.ENDC}")

		lstPages = dictCommPages[thisCommunity]["pages"]

		try:

			#set up our data holders
			lstRipeness = []
			lstViews = []
			lstAnnotations = []
			lstHotSpots = []
			lstURLs = []

			ripeHigh = 0
			viewHigh = 0
			viewTotal = 0
			viewCount = 0

			for thisPage in lstPages:

				#set the highs for ripe and views
				if int(thisPage["ripeness"]) > ripeHigh: 
					ripeHigh = int(thisPage["ripeness"])

				if int(thisPage["views"]) > viewHigh: 
					viewHigh = int(thisPage["views"])

				viewTotal += int(thisPage["views"])
				viewCount += 1

				lstRipeness.append(thisPage["ripeness"])
				lstViews.append(thisPage["views"])
				lstAnnotations.append(f'Title: {thisPage["title"]}\nViews: {thisPage["views"]}\nRipeness: {thisPage["ripeness"]}')
				lstURLs.append(thisPage["url"])

			#register the element tree
			ET.register_namespace("", "http://www.w3.org/2000/svg")

			#create a figure containing a single axes.
			fig, ax = plt.subplots(figsize=(24, 10), dpi=100)

			#ensure we create circles and not ovals
			plt.axis("equal")
			ax.axis("equal")

			#confgig plot
			plt.grid(which = "major", linestyle = "dashed")
			plt.title(f"{thisCommunity} Docs Ripeness Chart")
			plt.ylabel("Views")
			plt.xlabel("Days Published")

			#add the median lines
			ripeMedian = round(ripeHigh/2, 0)
			viewMedian = round(viewTotal/viewCount, 0)

			#add our break lines
			ax.axvline(ripeMedian, ymin=0, ymax=ripeHigh, label="Ripeness Mid-Point", color="green")
			ax.axvline(180, ymin=0, ymax=ripeHigh, label="Ripeness Mid-Point", color="red", linestyle="dashed", alpha=0.4)
			ax.axhline(viewMedian, xmin=0, xmax=viewHigh, label="View Mid-Point", color="green")

			#add text
			plt.text(15, 65, "New pages with high views.", fontsize=15, alpha=0.4, color="red")
			plt.text(15, 0, "New pages with low(er) views.", fontsize=15, alpha=0.4, color="red")
			plt.text(ripeMedian + 15.0, 65, "Old pages with high views.", fontsize=15, alpha=0.4, color="red")
			plt.text(ripeMedian + 15.0, 0, "Old pages with low views.", fontsize=15, alpha=0.4, color="red")

			#annotate roll over popups
			for idx, value in enumerate(lstRipeness):

				#get our marker (dot) coordinates
				floatX = lstRipeness[idx]
				floatY = lstViews[idx]

				strText = lstAnnotations[idx]
				ripeness = int(strText.split("Ripeness: ")[1])
				
				r = .1
				g = .5
				b = .1 #<--green
				a = .92 
				if ripeness > 90 and ripeness < 180: 
					r = 1.0 
					g = 0.7
					b = 0.1 #<--yellow
				elif ripeness > 179:
					r = .5
					g = .1
					b = .1 #<--red

				#each rollover is annotated to the ax subplot. The rollover content is not part of the pop over rectangle but a object that can be toggled on/off with Javascript. See annotate docs for explantion of the all the properties: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.annotate.html
				annotate = ax.annotate(lstAnnotations[idx], xy=(floatX, floatY), xytext=(0, 20), textcoords='offset points', color='w', ha='center', fontsize=10, bbox=dict(boxstyle='round4, pad=.9', fc=(r, g, b, a), ec=(1., 1., 1.), lw=1, zorder=1))

				
				thisCircle = plt.Circle((floatX, floatY), 0.5, color='blue', zorder=2)

				#add rects to list of hot spots
				lstHotSpots.append(thisCircle)

				#add each hotspot
				#patch = ax.add_patch(thisRect)
				patch = ax.add_patch(thisCircle)
				ax.add_patch(patch)
				
				#add a gid to the patch with identifiers for the patch and tool tip
				patch.set_gid(f'hotspot_{idx}')
				annotate.set_gid(f'tooltip_{idx}')

			#build plot
			plt.scatter(lstRipeness, lstViews, c="white")

			#show plot - use this for testing	  
			#plt.show()

			#move to GDrive
			dictGoogleServices = getGoogleServices()

			if dictGoogleServices["success"] == True: 

				driveService = dictGoogleServices["drive-service"]
				gmailService = dictGoogleServices["gmail-service"]
				pathToGoogle = os.path.expanduser("Google Drive/My Drive/")

				#check for main doc leads folder
				parentFolderId = manageGDriveDirectory(False, ET, driveService, "DocLeadReports", None, True)

				folderId = manageGDriveDirectory(False, ET, driveService, thisCommunity, parentFolderId, False)

				dictCommPages[thisCommunity]["folderId"] = folderId

				# #adding javascript calls to xml file
				f = BytesIO()
				dictXML = addSVGInteractivity(plt, ET, f, lstHotSpots, lstURLs, thisCommunity)
				xmlData = dictXML["xml"]
				tree = dictXML["tree"]

				# #create svg title
				today = datetime.now()
				strTitle = f"{thisCommunity}_{str(today.month)}-{str(today.day)}-{str(today.year)}"

				# #print SVG file to local 
				print(f"{cm.OKCYAN}Printed SVG file to {strRootPath}{strTitle}...{cm.ENDC}")
				xmlData.ElementTree(tree).write(f'{strRootPath}{strTitle}.svg')

				# #make sure the file was created
				if os.path.exists(f'{strRootPath}{strTitle}.svg') == True:

					#get mimetype of file
					# mimeType = None
					# mimeType = mimetypes.guess_type(f'{strRootPath}{strTitle}.svg')[0]

					print(f"{cm.OKCYAN}Uploading SVG file to GDrive...{cm.ENDC}")
					pathToGoogle = os.path.expanduser("Google Drive/My Drive/")
					if os.path.exists(f"{pathToGoogle}/DocLeadReports/{thisCommunity}/"):
						localPath = f'{strRootPath}{strTitle}.svg'
						remotePath = join(f"{pathToGoogle}/DocLeadReports/{thisCommunity}/{strTitle}.svg")

						if os.path.exists(remotePath) == False:
							dest = shutil.move(localPath, remotePath, copy_function = shutil.copytree)

			#close the plot
			plt.close()

			#send email message
			
			for thisDocLead in lstDocLeads:
				if thisDocLead["comm"] == thisCommunity: 
					strName = thisDocLead["name"]
					strTo = thisDocLead["email"]

					strLink = f"https://drive.google.com/drive/folders/{folderId}?usp=sharing"

					strBody = f"Hi {strName}\n\nTech Comms has created a Ripeness Matrix for your community pages on Konnect. A Ripeness Matrix combines the age of a page (number of days it has been published) and views into a scatter plot chart. The scatter plot is broken into four quadrants:\n\n•\tNew, high views\n•\tNew, low views\n•\tOld, high views\n•\tOld, low views\n\nThis provides you with some actionable data.\n•\tOld pages with low views should be reviewed to see if they are still relevant and, if needed, updated so their content is current for that topic. If no longer relevant they should be archived.\n•\tOld pages with high views should certainly be checked for relevancy and updated to make them current for that topic.\n•\tIf you have newer pages that are getting low views and that is not expected perhaps consider promoting those pages through Slack or email announcements.\n•\tNew pages with high views is perfect, right where you want to be.\n\nTo view the chart, which is an SVG file:\n\n•\tGo to: {strLink}\n•\tDownload the current svg file ({strTitle}.svg)\n•\tOpen the file in your browser.\n\nScrolling over any of the points in the chart will display the pages:\n\n•\tTitle\n•\tRipeness\n•\tViews\n\nClicking on the point will take you to that page in Konnect.\n\nIf you have any issues either accessing your matrix or how it functions reach out to me and let me know."

					strDate = f"{str(today.month)}-{str(today.day)}-{str(today.year)}"
					strSubject = f"{strDate} Ripeness Matrix for the {thisCommunity} community on Konnect" 

					sendGmail({"to":[strTo, "ssuranie@kargo.com"], "subject":strSubject, "body": strBody})

			#delete local file
			os.remove(f'{strRootPath}{strTitle}.svg')
			

		except Exception as e:

			exc_type, exc_obj, exc_tb = sys.exc_info()
			print(f"{cm.WARNING}Error!\nLine Number: {exc_tb.tb_lineno}\nMessage: {e}{cm.ENDC}")

def manageGDriveDirectory(bNeedsFile, ET, driveService, folderName, parentFolderId, isRoot):

	try:

		#check if folder exists - this only checks your drive!!!!!!
		print(f"{cm.OKGREEN}Checking if {folderName} folder exists...{cm.ENDC}")
		dictResults = gm.checkIfFolderExistsByName(driveService, folderName, driveId)
		folderId = None

		#create folder if it does not exists, return id for either case
		if dictResults["success"] == False:
			if isRoot == True:
				folderData = gm.createFolderInGDrive(driveService, folderName, None, driveId)
			else: 
				folderData = gm.createFolderInGDrive(driveService, folderName, parentFolderId, driveId)
			folderId = folderData["id"]
		else:
			folderId = dictResults["id"]

		#give folder permissions
		driveService.permissions().create(fileId=folderId, supportsAllDrives=True, body={"role": "reader", "type": "anyone"}).execute()

		return folderId

	except Exception as e:
		print(f"{cm.WARNING}There was an error creating either the {folderName} directory or the SVG file for it!\nMessage: {e}{cm.ENDC}")


def addSVGInteractivity(plt, ET, f, lstHotSpots, lstURLs, strComm):

	print(f"{cm.OKGREEN}Adding SVG Interactions...{cm.ENDC}")

	#save the figure
	plt.savefig(f, format="svg") 

	# Create XML tree from the SVG file.
	tree, xmlid = ET.XMLID(f.getvalue())
	tree.set('onload', 'init(event)')

	for i in lstHotSpots:

		# Get the index of the shape
		idx = lstHotSpots.index(i)
		
		#Hide the tooltips
		tooltip = xmlid[f'tooltip_{idx}']
		tooltip.set('visibility', 'hidden')

		# Assign onmouseover and onmouseout callbacks to patches.
		hotspot = xmlid[f'hotspot_{idx}']
		hotspot.set('onmouseover', "ShowTooltip(this)")
		hotspot.set('onmouseout', "HideTooltip(this)")
		hotspot.set('onmousedown', "OpenURL(this)")
		hotspot.set('onmouseup', 'c(this)')
		hotspot.set('myURL', lstURLs[idx])

		# This is the script defining the ShowTooltip and HideTooltip functions.
		script ="""
			<script type="text/ecmascript">
				<![CDATA[

					function init(event) {
						if ( window.svgDocument == null ) {
							svgDocument = event.target.ownerDocument;
						}
					}

					function ShowTooltip(obj) {
						var cur = obj.id.split("_")[1];
						var tip = svgDocument.getElementById('tooltip_' + cur);
						tip.setAttribute('visibility', "visible")
					}

					function HideTooltip(obj) {
						var cur = obj.id.split("_")[1];
						var tip = svgDocument.getElementById('tooltip_' + cur);
						tip.setAttribute('visibility', "hidden")
					}

					function OpenURL(obj) { 
						var myURL = obj.getAttribute('myURL');
						window.open(obj.getAttribute('myURL'), '_blank').focus();
					}


				]]>
			</script>
		"""
	#\\window.open(obj.myURL, '_blank').focus();
	print(f"{cm.OKGREEN}Printing SVG file for {strComm}...{cm.ENDC}")

	# Insert the script at the top of the file and save it.
	tree.insert(0, ET.XML(script))

	return {"xml":ET, "tree": tree}
	#ET.ElementTree(tree).write(f'{strRootPath}{strTitle}.svg')
	#print(f"{cm.OKCYAN}Printed SVG file to {strRootPath}{strTitle}...{cm.ENDC}")

def getGoogleServices():

	print(f"{cm.OKGREEN}Getting Google services...{cm.ENDC}")
	

	bSuccess = True
	strErr = ""

	#authenticate into Google
	print(f"{cm.OKGREEN}Authenticating with Google..{cm.ENDC}")

	dictResults = gm.getAuth()

    #if authentication fails
	if dictResults["success"] == False: 
		bSuccess = False
		strErr += f"\n{cm.WARNING}{dictResults['error-message']}{cm.ENDC}"
	else: 
		creds = dictResults["credentials"]

	#get gmail service
	dictGmailResults = gm.getService(creds,0)
	if dictGmailResults["success"] == False:
		bSuccess = False
		strErr += f"\n{cm.WARNING}{dictGmailResults['error-message']}{cm.ENDC}"
	else: 
		gmailService = dictGmailResults["service"]

	#get sheets service
	dictDriveResults = gm.getService(creds, 2)
	if dictDriveResults["success"] == False:
		bSuccess = False
		strErr += f"\n{cm.WARNING}{dictSheetsResults['error-message']}{cm.ENDC}"
	else: 
		driveService = dictDriveResults["service"]

	return {"success":bSuccess, "gmail-service":gmailService, "drive-service":driveService, "error-message": strErr}

def sendGmail(dictMailData):

	print(f"{cm.OKGREEN}Authenticating with Google..{cm.ENDC}")
	dictResults = gm.getAuth()

	if dictResults["success"] == False: 
		print(f"{cm.WARNING}There was an error autheticating into Google! \n{dictResults['error-message']}{cm.ENDC}")
	else: 

		print(f"{cm.OKGREEN}Successful Google Auth..{cm.ENDC}")
		creds = dictResults["credentials"]
		
		bSuccess = True
		dictGmailResults = gm.getService(creds,0)
		if dictGmailResults["success"] == False:
			bSuccess = False
			strErr += f"\n{cm.WARNING}{dictGmailResults['error-message']}{cm.ENDC}"
		else: 
			gmailService = dictGmailResults["service"]

		if bSuccess == False: 
			print(strErr)
		else:

			message = MIMEText(dictMailData["body"])
			message['to'] = ', '.join(dictMailData["to"])
			message['subject'] = dictMailData["subject"]
			create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

			try:
				message = (gmailService.users().messages().send(userId="me", body=create_message).execute())
				print(f'{cm.OKCYAN}Sent message to {message} Message Id: {message["id"]}{cm.ENDC}')
			except HTTPError as error:
				print(f'{cm.WARNING}An error occurred: {error}')
				message = None


#---------------APP START----------------------

if __name__ == '__main__':

	# lstCoords = makeCoords()
	# plotCoords(lstCoords)

	#retrieves the access token so we can be authenticated for additional calls. 
	print(f"{cm.OKGREEN}Logging into Interact API...{cm.ENDC}")
	dictAccess = kl.login()

	if "access_token" in dictAccess:  
		print(f"{cm.OKGREEN}Access token retrieved...{cm.ENDC}")
		konnectManager.accessToken = dictAccess["access_token"]
		lstPageMeta = []

		print(f"{cm.OKCYAN}Select CSV file...{cm.ENDC}")
		#csvFilePath = filedialog.askopenfilename()
		csvFilePath = "/Users/stevesuranie/Desktop/Kargo/Projects/Intranet/Data/Analytics/CSV/2024-02-16.csv"

		#get all Konnect pages
		lstPages = konnectManager.getAllPages()

		#get the unique page views for each page
		lstPageData = getUniquePageViews(lstPages, csvFilePath)

		lstCommunities = [d['comm'] for d in lstDocLeads]

		#get community pages
		dictCommPages = {}
		for thisCommunity in lstCommunities: 
			dictCommPages[thisCommunity] = {}
			lstPages = getCommunityPages(lstPageData, thisCommunity)
			dictCommPages[thisCommunity]["pages"] = lstPages
		
		#plot community pages
		plotCoords(dictCommPages)






