'''
Created on 24 Jan. 2019

@author: smithea3
'''
import csv
import itertools



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
                
    def createWarrantyStatusCSV(self, sFileName, results):
        self.assetDictionary = list(itertools.chain({**l,**c} for l in results for c in self.assetDictionary if l['sn']==c['sn']))
        with open(sFileName, 'w') as csvfile:
            fieldnames = ['Asset_Tag', 'sn', 'Manufacturer','Warranty_Status','Warranty_End_Date', 'pn']
            writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\n', fieldnames=fieldnames)
            writer.writeheader()
            for x in self.assetDictionary:
                writer.writerow(x)
    

                