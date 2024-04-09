#python script to access the interactgo api

import requests
import json
import datetime
import os
import csv

class KonnectLogin: 

    def __init__(self, strUserName, strPWD):
        self.strUserName = strUserName
        self.strPWD = strPWD

    def login(self):

        rootURL = "https://us-lb-api-01.interactgo.com/"
        tenantGuid = "5e1a83f8-6f9c-4bbc-af61-d1cccd11e925"

        dictHeader = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8", "Accept": "application/json", "X-Tenant":tenantGuid}
        dictBody = {
            "grant_type": "password", 
            "username":self.strUserName,
            "password":self.strPWD
        }

        response = requests.get(rootURL + "token", headers=dictHeader, data=dictBody)
        dictResponse = response.json()
        if "access_token" in dictResponse: 
            return {"sucess": True, "access_token": dictResponse["access_token"]}
        else: 
            return {"success": False, "msg":"There was an error getting the access token."}
