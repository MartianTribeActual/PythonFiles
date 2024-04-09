#this py file shows how to use our modules

#your script should sit one folder up from the modules folder so something like: 
# WorkingFolder/
#       your-script.py
#       modules/

#you need to have importlib installed - in Terminal pip importlib - if you have multiple instances of Python ensure 
#it is stored in the site-packages folder of the Python instance you work with. (Speaking from experience here)
#or - what I now do, I have shortcuts to all the site-packages directories in my Finder so they appear in the left nav
#of any window. When I pip some Python module I then go into the one they were downloaded into and copy/paste them into the other
#site package. The reason you may have more than one site-package is Apple pre-installs Python on your machine because 
#a lot of their apps use it. I went and installed it again with Homebrew which then made a mess of knowing what was getting 
#installed where. 

#ok, so once importlib is installed you can now import the modules in the site-packages folder as well as our own modules stored in 
#the modules folder in your working folder. Import the pip installed modules first, then use importlib to install the local modules. 

import os
import datetime
from datetime import date
import json
from jira import JIRA
from jira.client import ResultList
from jira.resources import Issue
import importlib

# import modules from relative paths
colors = importlib.import_module('modules.colors')
mondayManager = importlib.import_module('modules.mondayManager')
jiraManager = importlib.import_module('modules.jiraManager')
appManager = importlib.import_module('modules.appManager')

#our modules will need to be instantiated for you to use, some have classes, you can instantiate them like so: 

mm = mondayManager.MondayManager(mondayToken)
am = appManager.AppManager()
cm = colors.ColorManager()

#for the Monday module you'll need a token. You can get a token by: 
# 1. Log into Monday
# 2. Click on your icon
# 3. Select Developers from the options that display
# 4. In the Developer window, select My access tokens from the left nav
# 5. Your token will be here. Copy that. 

#In your script set up a variable and give it the token value: 

mondayToken = "eyJhbGciOiJIUzI1NiJ9.eyJ0aWQiOjI1Nj....."

#appManager is just a collection of functions that make life easier, such as date formatting or checking if an item exists. In order to use appmanager you #will need to have these modules installed in your site-package: os, datetime, csv, collections - I think these are all standard and come with Python but #check to make sure you have them. You can check your installed packages by running pip list in Terminal. 

#the colors module enables you to output to the Terminal window in different colors, like so: 
# print(f"{cm.OKGREEN}This is green text{cm.ENDC}") - examine the colors.py file to see available colors, feel free to add others, just follow the format there. 
#important: Always end the print out with the {cm.ENDC}, which resets the Terminal colors to the defaults. 

#BitBucket

#BitBucket is a source control site run by Atlassian and using Git as the underlying source control. Git allows multiple users to access a "repo" - kind of like a folder, but better. 

#Each user that has access to the repo can then clone it to a local repo on their machine and use and edit the files. You then use either the command line in Terminal or a Git client to commit and push the changes to the remote repo. Git works in branches. The main branch is called Master. The beauty of git is that enables users to make branches (copies) of Master or another branch and work locally on them without changing the Master files. When you are satisfied with the work on the branch you create a commit (basically a checkpoint in the branch) and push (upload) the commit to the remote repo. Now the remote repo will have your branch as part of the development tree. When you are ready to combine your code with the Master code you create a pull request on the remote repo (a PR is where you can assign/ask people to review your work, they can leave comments, you can make edits and commit those to the branch, etc.) and once the PR is accepted you merge it with the Master branch. You may have to resolve conflicts (where git is not sure if it should overwrite code in the Master file and wants you to select what to do). The last step is for you to ensure the local Master branch is now in sync with the remote Master branch by running "pulling" the remote Master branch. 


#the modules are in a repository on BitBucket. - https://bitbucket.org/ktc-ziggeo-app/kargopyrepo/src/master/ - this is a private repo, you need a invite to access it. If you have not been invited contact Steve Suranie. 

#clone (copy) this repo into your modules directory
#BitBucket recommends using SourceTree as your git client. It makes it pretty easy to clone and make changes to the repo. 

#You may have to set up SSH to clone it. You can do so by following the instructions below: 

#https://support.atlassian.com/bitbucket-cloud/docs/set-up-personal-ssh-keys-on-macos/

#How to use Monday Manager

#Monday's API does not use RESTFUL API verbs like GET or POST but instead uses GraphQL. This requires you not send a query to an endpoint but rather past a JSON file in the body of the request, the JSON file's key-value pairs are the hierarchy of what you are attempting to retrieve. So to get every board on the Monday site you would send this JSON: 

monQuery = '{ board }'

#This would return a ginormous JSON file. You could reduce the amount of data returned by being more specific: 

monQuery = '{ board (ids: [board1Id, board2Id])}'

#This would still return a lot of data but just from two boards. It's a bit hard to figure out at first but in the Monday Developers section there is a API Playground that let's you test a lot easier than writing and running Python code.

#This page can explain in better detail how to get the specific data you want: 
#https://developer.monday.com/api-reference/docs/introduction-to-graphql










