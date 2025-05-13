from datetime import date
from PyQt6 import QtCore, QtWidgets, QtGui
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import dex

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
        #opens the file selector
        self.file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Open iNatdex save (.csv)", "", "CSV Files (*.csv)")
        print(self.file_name[0])
        if(self.file_name[0] != ''):
            #tries to load the save, gives an error if something goes wrong
            try:
                dex.loadSave(self.file_name[0])
                dex.print_dex_config()
                dex.print_taxon_info()
                #opens the new window
                self.second_window = iNatdexWidget()
                self.second_window.show()
                self.close()
            except Exception as e:
                dlg = QMessageBox.critical(self,'iNatdex - Error','There was an error reading the save data.\nYou may have selected the wrong file.')
                #resets anything it might have read
                dex.username = ''
                dex.timeRangeStart = date.today()
                dex.timeRangeEnd = date.today()
                dex.quality_grades = 2
                dex.taxonInformation = []
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
        #opens file selector to select the .json
        self.file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Open iNaturalist list json (.json)", "", "JSON Files (*.json)")
        if(self.file_name[0] != ''):
            try:
                dex.taxonInformation = dex.get_all_taxa_info(self.file_name[0])
                dex.print_taxon_info()
                self.second_window = createOptionsWidget()
                self.second_window.show()
                self.close()
            except:
                dlg = QMessageBox.critical(self,'iNatdex - Error','There was an error reading the .json file.\nYou may have selected the wrong file.')
                #resets anything it might have read
                dex.taxonInformation = []

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
        dex.dexname = self.dexnameField.text()
        dex.username = self.usernameField.text()
        dex.savename = self.savenameField.text()
        dex.timeRangeStart = self.startDateField.date().toPyDate()
        dex.timeRangeEnd = self.endDateField.date().toPyDate()
        dex.useTheStartDate = self.useStartDate.isChecked()
        dex.useTheEndDate = self.useEndDate.isChecked()
        temp = self.qualityGradeField.currentText()
        if (temp == 'All observations'):
            dex.quality_grades = 1
        elif (temp == 'Verifiable observations'):
            dex.quality_grades = 2
        else:
            dex.quality_grades = 3
        dex.register_the_unregistered()
        temp_savefilepath = 'saves/'+dex.savename
        dex.saveList(temp_savefilepath)
        #opens the new window
        self.second_window = iNatdexWidget()
        self.second_window.show()
        self.close()
        
#The window that is the iNatdex visual representation
class iNatdexWidget(QtWidgets.QScrollArea):
        
    def __init__(self):
        super().__init__()
        
        widget = QWidget()
        registered_count = dex.count_registered_taxa()
        widget.resize(600, 400)
        self.taxaLayout = QGridLayout(widget)
        self.setWindowTitle("iNatdex - " + dex.dexname)
        self.setWindowIcon(QtGui.QIcon('assets/icon.ico'))
        self.titletext = QtWidgets.QLabel(dex.dexname)
        self.titletext.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.progressText = QtWidgets.QLabel("["+str(registered_count)+"/"+str(len(dex.taxonInformation))+"]")
        self.registerUnregisteredButton = QtWidgets.QPushButton("Check for newly registered taxa")
        self.unregisterRegisteredButton = QtWidgets.QPushButton("Check for newly unregistered taxa")
        #progress bar stuff
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setRange(0,len(dex.taxonInformation))
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
        #disables the buttons so they can't be clicked
        self.registerUnregisteredButton.setDisabled(True)#this happens too fast...
        self.unregisterRegisteredButton.setDisabled(True)
        #do the stuff with the API
        dex.register_the_unregistered()
        #save the list
        temp_savefilepath = 'saves/'+dex.savename
        dex.saveList(temp_savefilepath)
        #reenable the buttons
        self.registerUnregisteredButton.setDisabled(False)
        self.unregisterRegisteredButton.setDisabled(False)
        #next step is to refresh the buttons.
        self.deleteTaxonGrid()
        self.createTaxonGrid()
        #then refresh the progress bar & its text
        self.updateProgressBar()
        

    def unregRegClicked(self):
        #disables the buttons so they can't be clicked
        self.registerUnregisteredButton.setDisabled(True)
        self.unregisterRegisteredButton.setDisabled(True)
        #do the stuff with the API
        dex.unregister_the_registered()
        #save the list
        temp_savefilepath = 'saves/'+dex.savename
        dex.saveList(temp_savefilepath)
        #reenable the buttons
        self.registerUnregisteredButton.setDisabled(False)
        self.unregisterRegisteredButton.setDisabled(False)
        #next step is to refresh the buttons.
        self.deleteTaxonGrid()
        self.createTaxonGrid()
        #then refresh the progress bar & its text
        self.updateProgressBar()

    #updates the progress bar & its text
    def updateProgressBar(self):
        reg_count = dex.count_registered_taxa()
        self.progressText.setText("["+str(reg_count)+"/"+str(len(dex.taxonInformation))+"]")
        self.progressBar.setValue(reg_count)
    
    #creates the grid of buttons representing the inatdex
    def createTaxonGrid(self):
        count_of_squares = 0
        for i in range(4,40):
            if(count_of_squares >= len(dex.taxonInformation)):
                break
            for j in range(1,5):
                if(count_of_squares >= len(dex.taxonInformation)):
                    break
                commonName = dex.taxonInformation[count_of_squares][2]
                sciName = dex.taxonInformation[count_of_squares][1]
                currButt = QtWidgets.QPushButton(commonName+"\n"+sciName)
                if(dex.taxonInformation[count_of_squares][4]=="registered"):
                    currButt.setStyleSheet("background-color : #74ac00")
                self.taxaLayout.addWidget(currButt,i,j)
                count_of_squares+=1

    #deletes the grid of buttons representing the inatdex
    def deleteTaxonGrid(self):
        count_of_squares = 0
        for i in range (4,40):
            if(count_of_squares >= len(dex.taxonInformation)):
                break
            for j in range(1,5):
                if(count_of_squares >= len(dex.taxonInformation)):
                    break
                self.taxaLayout.itemAtPosition(i,j).widget().setParent(None)
                count_of_squares += 1