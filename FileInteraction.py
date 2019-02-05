'''
Created on 24 Jan. 2019

@author: smithea3
'''
import csv
import dateutil.parser
import itertools
import datetime


class FileController(object):
    '''
    classdocs
    '''


    def __init__(self, fileName):
        '''
        Constructor
        '''
        self.oFileName = fileName
        self.assetDictionary = []
        
        
    def buildAssetDictionary(self):
        with open(self.oFileName, newline='') as inFile:
            reader = csv.DictReader(inFile) 
            for row in reader:
                if ((row['Details_Table0_Manufacturer']=='HP') or (row['Details_Table0_Manufacturer']=='Hewlett-Packard')): # filter out non HP machines
                    # these field names map to SCCM - csv export of Hardware 01A report
                    self.assetDictionary.append(
                        { 'sn' : row['Details_Table0_SerialNumber'], 
                         'Asset_Tag' : row['Details_Table0_ComputerName'], 
                         'Manufacturer' : row['Details_Table0_Manufacturer'], 
                         'pn' : ''
                         })  # create dictionary
                else:
                    continue
    '''            
    def compileResults(self, results):
        returnList = []
        for r in results:
            warrantyEndDate = ''
            warrantyStatus = 'No warranty'
            serialNumber = r['product']['serialNumber']
            # documentation for JSON fields available at HP Developers portal
            for offer in r['offers']:
                try:  # try_catch block in case missing records or incomplete records are returned
                   
                    if (offer['offerDescription'] == 'HWM Onsite'): # only check HWM Onsite for valid warranty - believe this to be the accurate record 
                            warrantyEndDate += offer['serviceObligationLineItemEndDate']
                            parsed = dateutil.parser.parse(offer['serviceObligationLineItemEndDate']).date()
                            todaysDate = datetime.date.today()
                            if todaysDate < parsed: # active warranty
                                warrantyStatus = 'Warranty active'
                            else: # expired warranty
                                warrantyStatus = 'Warranty Expired'
                            
                except: # missing records
                    warrantyStatus = 'ERR: unable to retrieve'
                    warrantyEndDate = 'ERR: unable to retrieve'
            returnList.append({'sn' : serialNumber, 
                               'Warranty_Status' : warrantyStatus, 
                               'Warranty_End_Date' : warrantyEndDate})
        
        self.assetDictionary = list(itertools.chain({**l,**c} for l in returnList for c in self.assetDictionary if l['sn']==c['sn']))
    '''
             
                
                
    def createWarrantyStatusCSV(self, sFileName, results):
        self.assetDictionary = list(itertools.chain({**l,**c} for l in results for c in self.assetDictionary if l['sn']==c['sn']))
        with open(sFileName, 'w') as csvfile:
            fieldnames = ['Asset_Tag', 'sn', 'Manufacturer','Warranty_Status','Warranty_End_Date', 'pn']
            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=fieldnames)
            writer.writeheader()
            for x in self.assetDictionary:
                writer.writerow(x)
    

                