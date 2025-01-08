import sys, json, csv
from pyinaturalist import *
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import ijson

client = iNatClient()

#the list that has taxon IDs and other info
taxonInformation = []
#data relating to the list
dexname = 'New iNatdex'
username = 'username'
timeRangeStart = date(2024, 1, 1)
timeRangeEnd = date.today()
useTheStartDate = True
useTheEndDate = False
#the quality grades to include: (1 is all, 2 is verifiable, 3 is research grade only)
quality_grades = 2
#name of save file
savename = 'test1.csv'

#fills up a 2D list with information about each taxa.
def get_all_taxa_info(listfilepath):
    infoList = []
    file = open(listfilepath, encoding="utf8")
    entries = ijson.items(file, 'listed_taxa.item')
    for entry in entries:
        rowdata = []
        rowdata.append(entry['taxon_id'])
        rowdata.append(entry['taxon']['name'])
        rowdata.append(entry['taxon']['default_name']['name'])
        rowdata.append(entry['taxon']['iconic_taxon_name'])
        rowdata.append('unregistered')
        infoList.append(rowdata)
    return infoList

#the count of observations matching the dex inclusion criteria + the specified taxon_id
def count_dex_included_observations(taxon_id_num):
    #global variables
    global taxonInformation
    global dexname
    global username
    global timeRangeStart
    global timeRangeEnd
    global useTheStartDate
    global useTheEndDate
    global quality_grades
    global savename
    #the value it returns
    returnValue = 0
    #this part decides what the start/end dates should be
    if (useTheStartDate == False):
        startDate = date(1900, 1, 1)
    else:
        startDate = timeRangeStart
    if (useTheEndDate == False):
        endDate = date(2200,1,1)
    else:
        endDate = timeRangeEnd
    #this part actually does the search on iNaturalist
    if (int(quality_grades) == 1):
        returnValue = get_observations(user_id=username,taxon_id=taxon_id_num,d1=startDate,d2=endDate,count_only=True)['total_results']
    elif (int(quality_grades) == 2):
        returnValue = get_observations(user_id=username,taxon_id=taxon_id_num,d1=startDate,d2=endDate,count_only=True,verifiable=True)['total_results']
    elif (int(quality_grades) == 3):
        returnValue = get_observations(user_id=username,taxon_id=taxon_id_num,d1=startDate,d2=endDate,count_only=True,quality_grade='research')['total_results']
    return returnValue
    
#checks for any unregistered taxa that have become registered
def register_the_unregistered():
    #global variables
    global taxonInformation
    global dexname
    global username
    global timeRangeStart
    global timeRangeEnd
    global useTheStartDate
    global useTheEndDate
    global quality_grades
    global savename
    for entry in taxonInformation:
        if entry[4] == 'unregistered':
            if(count_dex_included_observations(entry[0]) > 0):
                entry[4] = 'registered'

#checks for any registered taxa that have since been unregistered
def unregister_the_registered():
    #global variables
    global taxonInformation
    global dexname
    global username
    global timeRangeStart
    global timeRangeEnd
    global useTheStartDate
    global useTheEndDate
    global quality_grades
    global savename
    for entry in taxonInformation:
        if entry[4] == 'registered':
            print(entry[1])
            print(count_dex_included_observations(entry[0]))
            if(count_dex_included_observations(entry[0]) <= 0):
                entry[4] = 'unregistered'
                print('gone')

#counts how many registered entries there are
def count_registered_taxa():
    regCount = 0
    for entry in taxonInformation:
        if entry[4] == 'registered':
            regCount = regCount + 1
    return regCount
    
  
#prints the list of taxa info in a readable format
def print_taxon_info():
    for entry in taxonInformation:
        print(str(entry[0]) + ' ' + entry[1] + ' ' + entry[2] + ' ' + str(entry[3]) + ' ' + entry[4])

#prints the dex inclusion configuration
def print_dex_config():
    output = 'dexname: '+ dexname + '\nusername: ' + username + '\nquality grades: ' + str(quality_grades) + '\nobserved after: ' + str(timeRangeStart) + '\nobserved before: '+ str(timeRangeEnd) + '\nuse start date: ' + str(useTheStartDate) +'\nuse end date: '+  str(useTheEndDate)+ '\nsave file name: ' + savename
    print(output)
    return output

#saves the list to a csv
def saveList(savefile_path):
    #global variables
    global taxonInformation
    global dexname
    global username
    global timeRangeStart
    global timeRangeEnd
    global useTheStartDate
    global useTheEndDate
    global quality_grades
    global savename
    with open(savefile_path, 'w', newline='') as csvfile:
        savewriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        savewriter.writerow([dexname,username,timeRangeStart,timeRangeEnd,useTheStartDate,useTheEndDate,quality_grades,savename])
        for entry in taxonInformation:
            savewriter.writerow([entry[0],entry[1],entry[2],entry[3],entry[4]])
        csvfile.close()

#loads stuff from the savefile csv
def loadSave(savefile_path):
    #global variables
    global taxonInformation
    global dexname
    global username
    global timeRangeStart
    global timeRangeEnd
    global useTheStartDate
    global useTheEndDate
    global quality_grades
    global savename
    
    #set up the reader
    with open(savefile_path, newline='') as csvfile:
        savereader = csv.reader(csvfile, delimiter=',', quotechar='|')
        #Read the data from the first row
        firstline = next(savereader)
        dexname = firstline[0]
        username = firstline[1]
        timeRangeStart = firstline[2]
        timeRangeEnd = firstline[3]
        useTheStartDate = firstline[4]
        useTheEndDate = firstline[5]
        quality_grades = firstline[6]
        savename = firstline[7]
        #Read the data from the rest of the rows (the taxa on the list)
        for row in savereader:
            taxonInformation.append(row)
        csvfile.close()

#GUI STUFF

#This is the window that opens when the app is opened
class startupWidget(QtWidgets.QWidget):
    
    def __init__(self):
        super().__init__()

        self.resize(300, 100)
        self.setWindowTitle("iNatdex Startup")
        self.setWindowIcon(QtGui.QIcon('assets/icon.ico'))
        self.loadButton = QtWidgets.QPushButton("Load existing dex")
        self.createButton = QtWidgets.QPushButton("Create new dex")
        self.text = QtWidgets.QLabel("iNatdex")
        self.text.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter) 
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.loadButton)
        self.layout.addWidget(self.createButton)
        
        self.loadButton.clicked.connect(self.loadButtonClicked)
        self.createButton.clicked.connect(self.createButtonClicked)

    #for loading the save when load button is clicked
    def loadButtonClicked(self):
        #global variables
        global dexname
        global username
        global timeRangeStart
        global timeRangeEnd
        global quality_grades
        global taxonInformation
        #opens the file selector
        self.file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Open iNatdex save (.csv)", "", "CSV Files (*.csv)")
        print(self.file_name[0])
        if(self.file_name[0] != ''):
            #tries to load the save, gives an error if something goes wrong
            try:
                loadSave(self.file_name[0])
                print_dex_config()
                print_taxon_info()
                #opens the new window
                self.second_window = iNatdexWidget()
                self.second_window.show()
                self.close()
            except Exception as e:
                dlg = QMessageBox.critical(self,'iNatdex - Error','There was an error reading the save data.\nYou may have selected the wrong file.')
                #resets anything it might have read
                username = ''
                timeRangeStart = date.today()
                timeRangeEnd = date.today()
                quality_grades = 2
                taxonInformation = []
                print(e)
            
    def createButtonClicked(self):
        self.second_window = creationWidget()
        self.second_window.show()
        self.close()

#The window that comes up when creating a new dex
class creationWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        

        self.resize(300, 100)
        self.setWindowTitle("Create new dex")
        self.setWindowIcon(QtGui.QIcon('assets/icon.ico'))
        self.backButton = QtWidgets.QPushButton("Back to startup")
        self.jsonLoadButton = QtWidgets.QPushButton("Load JSON File")
        self.text = QtWidgets.QLabel('To create a new dex, you need to have the .JSON file\nfor the iNaturalist list you want to use for the dex.\nFor instructions how to get it, see instructions.pdf')
        self.text.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.jsonLoadButton)
        self.layout.addWidget(self.backButton)

        self.backButton.clicked.connect(self.backButtonClicked)
        self.jsonLoadButton.clicked.connect(self.jsonLoadButtonClicked)

    def backButtonClicked(self):
        self.second_window = startupWidget()
        self.second_window.show()
        self.close()

    def jsonLoadButtonClicked(self):
        #global variable
        global taxonInformation
        #opens file selector to select the .json
        self.file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Open iNaturalist list json (.json)", "", "JSON Files (*.json)")
        if(self.file_name[0] != ''):
            try:
                taxonInformation = get_all_taxa_info(self.file_name[0])
                print_taxon_info()
                self.second_window = createOptionsWidget()
                self.second_window.show()
                self.close()
            except:
                dlg = QMessageBox.critical(self,'iNatdex - Error','There was an error reading the .json file.\nYou may have selected the wrong file.')
                #resets anything it might have read
                taxonInformation = []

#The window that comes up after reading a list JSON to give the options for the dex settings
class createOptionsWidget(QtWidgets.QWidget):
    def __init__(self):

        super().__init__()

        self.resize(300, 100)
        self.setWindowTitle('New dex settings')
        self.setWindowIcon(QtGui.QIcon('assets/icon.ico'))
        self.layout = QFormLayout(self)

        #the options
        self.dexnameField = QLineEdit('New iNatdex', parent = self)
        self.usernameField = QLineEdit('username', parent = self)
        self.qualityGradeField = QComboBox()
        self.qualityGradeField.addItems(['All observations', 'Verifiable observations', 'Research Grade only'])
        self.useStartDate = QCheckBox('Use start date', self)
        self.useEndDate = QCheckBox('Use end date', self)
        self.startDateField = QDateEdit(date.today())
        self.endDateField = QDateEdit(date(2100, 12, 1))
        self.startDateField.setDisabled(True)
        self.endDateField.setDisabled(True)
        self.savenameField = QLineEdit('newinatdex.csv', parent = self)
        self.finishButton = QtWidgets.QPushButton('Finish Setup')
        self.cancelButton = QtWidgets.QPushButton('Cancel')
        #adding them to the window
        self.layout.addRow('Dex Name', self.dexnameField)
        self.layout.addRow('Username', self.usernameField)
        self.layout.addRow('Quality Grade', self.qualityGradeField)
        self.layout.addRow('Date Range Settings', self.useStartDate)
        self.layout.addRow('', self.useEndDate)
        self.layout.addRow('Start Date (MM/DD/YYYY)', self.startDateField)
        self.layout.addRow('End Date (MM/DD/YYYY)', self.endDateField)
        self.layout.addRow('Savefile Name', self.savenameField)
        self.layout.addRow(self.cancelButton, self.finishButton)
        #the date checkboxes enabling/disabling their respective QDateEdits
        self.useStartDate.stateChanged.connect(lambda:self.startDateField.setDisabled(self.startDateField.isEnabled()))
        self.useEndDate.stateChanged.connect(lambda:self.endDateField.setDisabled(self.endDateField.isEnabled()))
        #the buttons' connections
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.finishButton.clicked.connect(self.finishButtonClicked)

    def cancelButtonClicked(self):
        self.second_window = creationWidget()
        self.second_window.show()
        self.close()

    def finishButtonClicked(self):
        #global variables
        global dexname
        global username
        global timeRangeStart
        global timeRangeEnd
        global quality_grades
        global savename
        global useTheStartDate
        global useTheEndDate

        #first check if the input is valid
        if(',' in self.dexnameField.text() or ',' in self.usernameField.text() or ',' in self.savenameField.text()):
            dlg = QMessageBox.critical(self,'iNatdex - Error','Dex name, username, and save name cannot contain commas.')
            return
        if(self.startDateField.isEnabled() and self.endDateField.isEnabled() and self.startDateField.date() > self.endDateField.date()):
            dlg = QMessageBox.critical(self,'iNatdex - Error','Start date cannot be after the end date.')
            return
        if(self.savenameField.text()[-4:].upper() != '.CSV'):
           dlg = QMessageBox.critical(self,'iNatdex - Error','Savefile name must end in ".csv"')
           return
        #put the values into the variables
        self.finishButton.setDisabled(True)
        dexname = self.dexnameField.text()
        username = self.usernameField.text()
        savename = self.savenameField.text()
        timeRangeStart = self.startDateField.date().toPyDate()
        timeRangeEnd = self.endDateField.date().toPyDate()
        useTheStartDate = self.useStartDate.isChecked()
        useTheEndDate = self.useEndDate.isChecked()
        temp = self.qualityGradeField.currentText()
        if (temp == 'All observations'):
            quality_grades = 1
        elif (temp == 'Verifiable observations'):
            quality_grades = 2
        else:
            quality_grades = 3
        register_the_unregistered()
        temp_savefilepath = 'saves/'+savename
        saveList(temp_savefilepath)
        #opens the new window
        self.second_window = iNatdexWidget()
        self.second_window.show()
        self.close()
        
#The window that is the iNatdex visual representation
class iNatdexWidget(QtWidgets.QScrollArea):
        
    def __init__(self):
        super().__init__()
        
        widget = QWidget()
        registered_count = count_registered_taxa()
        widget.resize(600, 400)
        self.taxaLayout = QGridLayout(widget)
        self.setWindowTitle("iNatdex - " + dexname)
        self.setWindowIcon(QtGui.QIcon('assets/icon.ico'))
        self.titletext = QtWidgets.QLabel(dexname)
        self.titletext.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.progressText = QtWidgets.QLabel("["+str(registered_count)+"/"+str(len(taxonInformation))+"]")
        self.registerUnregisteredButton = QtWidgets.QPushButton("Check for newly registered taxa")
        self.unregisterRegisteredButton = QtWidgets.QPushButton("Check for newly unregistered taxa")
        #progress bar stuff
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0,len(taxonInformation))
        self.progressBar.setValue(registered_count)
        self.taxaLayout.addWidget(self.titletext,1,1)
        self.taxaLayout.addWidget(self.progressBar,2,1)
        self.taxaLayout.addWidget(self.progressText,2,2)
        self.taxaLayout.addWidget(self.registerUnregisteredButton,3,1)
        self.taxaLayout.addWidget(self.unregisterRegisteredButton,3,2)
        #does the grid of taxons
        self.createTaxonGrid()
        self.setWidget(widget)
        self.setWidgetResizable(True)
        #enables stretching of the columns
        self.taxaLayout.setColumnStretch(1, 1)
        self.taxaLayout.setColumnStretch(2, 1)
        self.taxaLayout.setColumnStretch(3, 1)
        self.taxaLayout.setColumnStretch(4, 1)
        #connects the register/unregister buttons
        self.registerUnregisteredButton.clicked.connect(self.regUnregClicked)
        self.unregisterRegisteredButton.clicked.connect(self.unregRegClicked)

    def regUnregClicked(self):
        global savename
        #disables the buttons so they can't be clicked
        self.registerUnregisteredButton.setDisabled(True)#this happens too fast...
        self.unregisterRegisteredButton.setDisabled(True)
        #do the stuff with the API
        register_the_unregistered()
        #save the list
        temp_savefilepath = 'saves/'+savename
        saveList(temp_savefilepath)
        #reenable the buttons
        self.registerUnregisteredButton.setDisabled(False)
        self.unregisterRegisteredButton.setDisabled(False)
        #next step is to refresh the buttons.
        self.deleteTaxonGrid()
        self.createTaxonGrid()

    def unregRegClicked(self):
        #disables the buttons so they can't be clicked
        self.registerUnregisteredButton.setDisabled(True)
        self.unregisterRegisteredButton.setDisabled(True)
        #do the stuff with the API
        unregister_the_registered()
        #save the list
        temp_savefilepath = 'saves/'+savename
        saveList(temp_savefilepath)
        #reenable the buttons
        self.registerUnregisteredButton.setDisabled(False)
        self.unregisterRegisteredButton.setDisabled(False)
        #next step is to refresh the buttons.
        self.deleteTaxonGrid()
        self.createTaxonGrid()
        
    #creates the grid of buttons representing the inatdex
    def createTaxonGrid(self):
        count_of_squares = 0
        for i in range(4,40):
            if(count_of_squares >= len(taxonInformation)):
                break
            for j in range(1,5):
                if(count_of_squares >= len(taxonInformation)):
                    break
                commonName = taxonInformation[count_of_squares][2]
                sciName = taxonInformation[count_of_squares][1]
                currButt = QtWidgets.QPushButton(commonName+"\n"+sciName)
                if(taxonInformation[count_of_squares][4]=="registered"):
                    currButt.setStyleSheet("background-color : #74ac00")
                self.taxaLayout.addWidget(currButt,i,j)
                count_of_squares+=1

    #deletes the grid of buttons representing the inatdex
    def deleteTaxonGrid(self):
        global taxonInformation
        count_of_squares = 0
        for i in range (4,40):
            if(count_of_squares >= len(taxonInformation)):
                break
            for j in range(1,5):
                if(count_of_squares >= len(taxonInformation)):
                    break
                self.taxaLayout.itemAtPosition(i,j).widget().setParent(None)
                count_of_squares += 1
   


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationName('iNatDex')
    widget = startupWidget()
    widget.show()
    sys.exit(app.exec())

