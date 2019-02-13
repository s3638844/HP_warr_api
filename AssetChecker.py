'''
Created on 24 Jan. 2019

@author: smithea3
'''
import requests
import json
import time
import dateutil.parser
import datetime


class APIinteraction(object):
    '''
    classdocs
    
    contains functions for interacting with HP's warranty API.  
    
    Token and JSON related code sourced from example code provided from HP.
    
    Remainder has been adapted and rewritten to be modular from same example
     
    '''

    def __init__(self, assetDictionary):
        '''
        Constructor
        '''
        self.url = 'https://css.api.hp.com'
        self.assetDictionary = assetDictionary
        self.apiKey = ''
        self.apiSecret = ''
        self.token = ''
        self.job = ''
        self.results = ''
        
    # get token from HP API using Key and Secret    
    def getToken(self):
        tokenBody = { 'apiKey': self.apiKey, 'apiSecret': self.apiSecret, 'grantType': 'client_credentials', 'scope': 'warranty' }
        tokenHeaders = { 'Accept': 'application/json' }
        tokenResponse = requests.post((self.url + '/oauth/v1/token'), data=tokenBody, headers=tokenHeaders)
        tokenJson = tokenResponse.json()
        self.token = tokenJson['access_token']
        
    # creates batch job and sends request to HP      
    def batchJob(self):
        jobHeaders = {
        'Accept': 'application/json',
        'Authorization': 'Bearer ' + self.token,
        'Content-Type': 'application/json'
        }
        print('Creating new batch job...')
        self.job = requests.post(self.url + '/productWarranty/v2/jobs/', data=json.dumps(self.assetDictionary), headers=jobHeaders).json()
        # Feedback to console for user
        print('Batch job created successfully.')
        print('--------------------')
        print('Job ID: ' + self.job['jobId'])
        print('Estimated time in seconds to completion: ' + str(self.job['estimatedTime']))
        print('')
        if (self.job['estimatedTime'] > 1200):
            time.sleep(40)
        else:
            time.sleep(20)

    def jobMonitor(self):
        
        headers = {
        'Authorization': 'Bearer ' + self.token,
        'Accept-Encoding': 'gzip,deflate'
        }
        status = 'incomplete'
        
        while (status == 'incomplete'):
            monitorResponse = requests.get(self.url + '/productWarranty/v2/jobs/' + self.job['jobId'], headers=headers)
            monitor = monitorResponse.json()
            
            if (monitor['status'] != "completed"):
                
                if (monitor['estimatedTime'] > 1200):
                    print(monitor)
                    print('Estimated time in seconds to completion: ' + str(monitor['estimatedTime']) + '\nNext job check in 10 minutes...\n')
                    
                    time.sleep(200)
                    
                elif (monitor['estimatedTime'] > 600):
                    print(monitor)
                    print('Estimated time in seconds to completion: ' + str(monitor['estimatedTime']) + '\nNext job check in 5 minutes...\n')
                    time.sleep(100)
                    
                else:
                    print(monitor)
                    print('Estimated time in seconds to completion: ' + str(monitor['estimatedTime']) + '\nNext job check in 1 minute...\n')
                    time.sleep(10)
                    
            else:
                status = 'complete'
                
        self.results = requests.get(self.url + '/productWarranty/v2/jobs/' + self.job['jobId'] + '/results', headers=headers).json()
        print('Batch job complete: \n')


        
    def createJSONFile(self, sFileSaveLoc):
        try:
            with open(sFileSaveLoc + self.job['jobId'] + '.json', 'w') as outFile:
                json.dump(self.results, outFile)
                
        except Exception as e:
            print(e)   
                      
                      
                      
    def compileResults(self):
        returnList = []
        todaysDate = datetime.date.today()
        
        for r in self.results:
            warrantyStatus = 'No warranty'
            serialNumber = r['product']['serialNumber']
            # documentation for JSON fields available at HP Developers portal
              
            for offer in r['offers']:
                try:
                    if (offer.get('serviceObligationLineItemEndDate') and not (offer['offerDescription'] == 'Wty: HP Support for Initial Setup')):
                        endDateParsed = dateutil.parser.parse(offer['serviceObligationLineItemEndDate']).date()
                        if (endDateParsed > todaysDate):
                            warrantyStatus = 'Warranty active'
                            warrantyEndDate = endDateParsed
                             
                        elif (endDateParsed < todaysDate):
                            warrantyStatus = 'Warranty Expired'
                            warrantyEndDate = endDateParsed
                            
                        
                 
                except:  # missing records
                    warrantyStatus = 'ERR: unable to retrieve'
                    warrantyEndDate = 'ERR: unable to retrieve'
            returnList.append({'sn' : serialNumber,
                               'Warranty_Status' : warrantyStatus,
                               'Warranty_End_Date' : warrantyEndDate})
        self.results = returnList                              
                                
