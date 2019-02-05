from tkinter import filedialog, Label, Button, messagebox
import tkinter as tk
import AssetChecker
import FileInteraction


class WarrCheckGUI(tk.Tk):
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.oFileName=''  # file to be opened
        self.sFileSaveLoc='' # save file directory
        self.sFileName='Warranty_Output.csv' # file to be saved
        self.label = Label(self, text=
               '''INSTRUCTIONS FOR USE:
               1. Select 'Browse for file' and select your Hardware 01A report exported as a CSV file.
               2. Select 'Send Query to HP' 
               3. While in progress this app will track estimated time to completion of query 
               4. Once complete app will prompt you to save your export, please save as CSV
               NB. Disconnecting from network while in progress or exit app will cause query to fail
               NBB. HARDWARE 01A report must be an unmodified CSV export from SCCM''').pack()

        self.openButton = Button(self, text='Browse for file', command=self.openFile).pack()
        self.sendButton = Button(self, text='Send Query to HP', command=self.sendQuery).pack()

        self.mainloop()


    def openFile(self):
        self.oFileName = filedialog.askopenfilename(title="Choose CSV file")
        
    def sendQuery(self): 
        
        try:
            fi = FileInteraction.FileController(self.oFileName) # create file interaction object 
            fi.buildAssetDictionary() # build the asset dictionary to be sent to HP
            self.sFileSaveLoc = filedialog.askdirectory() + '/' # ask user to select directory for file to be saved.
            self.sFileName = self.sFileSaveLoc + self.sFileName  # append filename to location
            
            api = AssetChecker.APIinteraction(fi.assetDictionary) # create the API interaction object
            api.getToken() # get a token from HP
            api.batchJob() # start a batch job using previously supplied assetDictionary
            api.jobMonitor() # monitor the ongoing batch job until completion
            api.createJSONFile(self.sFileSaveLoc)
            
            api.compileResults(api.results) # compile 
            fi.createWarrantyStatusCSV(self.sFileName, api.results)
            
        except:
            messagebox.showerror("ERROR", "Please select Report file using 'Browse for File' First")  # this is a catchall at this stage needs to be refined for various types of exceptions
        
        
        
    
    
    
if __name__ == '__main__':
    WarrCheckGUI()
        