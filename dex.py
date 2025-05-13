import sys, json, csv
from pyinaturalist import *
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