#####################################################################################################################################
# Check StudyIDs on the File Server
# Created by: Joel Anderton
# Created date: 6/11/2019
# Updated date: 6/11/2019
#
# Purpose: Check that the OFC2 StudyIDs that name the files on the file server match the IDs in SQL
#          Check they did what they were suppose to do
#          Check they are in the correct folder
#          Check they contain all the right files
# Updates:
#
#####################################################################################################################################

from tkinter import *
from tkinter import ttk
import pypyodbc
import os
import re
import sys
import csv
import re
import datetime


def sql_connection():
    """Creates a SQL connection"""
    connection_string = ('Driver={SQL Server};' 
                         'Server=       ;'
			             'Database=OFC2;' 
			             'Trusted_Connection=Yes')
    connection = pypyodbc.connect(connection_string)
    return connection


def get_file_paths(drive, phenotype):
    phenotype_paths = {'R:':{'LipUltrasound':r'R:\OFC2\PhenotypeRating\OOM', 
                    'LipPhotos':r'R:\OFC2\PhenotypeRating\LipPhotos',
                    'LHFPhoto':r'R:\OFC2\PhenotypeRating\WoundHealingPhotos',
                    'IntraoralPhotos':r'R:\OFC2\PhenotypeRating\IntraOralPhotos',
                    'PalateVideo':r'R:\OFC2\PhenotypeRating\PalateVideos',
                    'Photos3D':r'R:\OFC2\PhenotypeRating\3DImages',
                    'DentalImpression':'R:\OFC2\PhenotypeRating\DentalCast',
                    'HandScan':r'R:\OFC2\PhenotypeRating\Hand Scan',
                    'SpeechVideos':r'R:\OFC2\PhenotypeRating\SpeechVideos'
                    },
                     'P:':{'LipUltrasound':r'P:\OFC2\Phenotype Images Archive\OOM', 
                    'LipPhotos':r'P:\OFC2\Phenotype Images Archive\LipPhotos',
                    'LHFPhoto':r'P:\OFC2\Phenotype Images Archive\WoundHealingPhotos',
                    'IntraoralPhotos':r'P:\OFC2\Phenotype Images Archive\IntraOralPhotos',
                    'PalateVideo':r'P:\OFC2\Phenotype Images Archive\PalateVideos',
                    'Photos3D':r'P:\OFC2\Phenotype Images Archive\3DImages',
                    'DentalImpression':'P:\OFC2\Phenotype Images Archive\DentalCast',
                    'HandScan':r'P:\OFC2\Phenotype Images Archive\Hand Scan',
                    'SpeechVideos':r'P:\OFC2\Phenotype Images Archive\SpeechVideos'
                    }}
    print(phenotype_paths[drive][phenotype])
    return phenotype_paths[drive][phenotype]


def get_studyIDs_SQL(phenotype, studyID=None):
    """Finds completed StudyIDs in SQL"""
    print('\nSearching SQL for StudyIDs')
    studyID_list = []
    studyID_list.append(studyID)
    connection = sql_connection()
    cur = connection.cursor()

    if studyID == None: # if not given an individual StudyID
        sqlcode = ('''  
        SELECT 
         [StudyID]
       
        FROM IndividualChecklistExported
        WHERE {0} = 1
        '''.format(phenotype))
        cur.execute(sqlcode)
    else: # if given an individual StudyID
        sqlcode = ('''  
        SELECT 
         [StudyID]
       
        FROM IndividualChecklistExported
        WHERE {0} = 1 AND [StudyID] = ?
        '''.format(phenotype))
        cur.execute(sqlcode, studyID_list)

    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        print('StudyID: {0}'.format(row[0:][0]), end='\r')
        studyIDs_in_SQl_list.append(row[0:][0])
    print('StudyID: Done!     ')
    print()
    return studyIDs_in_SQl_list


def get_studyIDs_Server(drive, phenotype, studyID = None):
    """Finds StudyIDs used on file server"""
    print('\nSearching file server in the {0} phenotype folder for StudyIDs'.format(phenotype))
 
    path = get_file_paths(drive, phenotype)

    studyID_list = []
    if studyID == None:
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                match = re.search("[A-Za-z]{2}[0-9]{5}", dir)    
                if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                    print('StudyID:', dir[match.start():match.end()], end='\r')
                    studyID_list.append({dir[match.start():match.end()]:os.path.join(root, dir[match.start():match.end()])}) 
    else:
        for root, dirs, files in os.walk(path):
            if studyID in dirs:
                for dir in dirs:
                    match = re.search("[A-Za-z]{2}[0-9]{5}", dir)    
                    if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                        print('StudyID:', dir[match.start():match.end()], end='\r')
                        studyID_list.append({dir[match.start():match.end()]:os.path.join(root, dir[match.start():match.end()])})
    print('StudyID: Done!     ')
    print()
    return studyID_list


def check_folder(drive, phenotype, studyID = None):
    """Check if file is in the correct folder"""
    print('************************************\nFolder Check for {0}\n************************************'.format(phenotype))
    path = get_file_paths(drive, phenotype)
        
    wrong_folder = []

    if studyID == None:
        for root, dirs, files in os.walk(path):
            for file in files:
                match = re.search("[A-Za-z]{2}[0-9]{5}", file) 
                if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                    print('Checking files for:', file[match.start():match.end()], end='\r')
                    if file[match.start():match.end()] not in root:
                       wrong_folder.append(os.path.join(root, file))
    else:
        for root, dirs, files in os.walk(path):
            if studyID in root:
                for file in files:
                    match = re.search("[A-Za-z]{2}[0-9]{5}", file) 
                    if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                        print('Checking files for:', file[match.start():match.end()], end='\r')
                        if file[match.start():match.end()] not in root:
                           wrong_folder.append(os.path.join(root, file))

    if len(wrong_folder) >0:
        print('Check that the file is in the correct folder for the following:')
        for file in wrong_folder:
            print(file)
    else:
        print('All files are in their correct folders!')
    #return wrong_folder

def check_spelling(drive, phenotype, studyID = None):
    """Check if file has the correct spelling for a StudyID"""
    print('************************************\nSpelling Check\n************************************')
    diff = []
    studyIDs_and_paths = get_studyIDs_Server(drive=drive, phenotype=phenotype, studyID=studyID)

    # Extracts folders and folder paths:
    studyIDs_on_Server = []
    folder_paths = {}
    for folders in studyIDs_and_paths:
        for folder, path in folders.items():
            studyIDs_on_Server.append(folder)
            folder_paths.update({folder : path})

    # Gets accectable StudyIDs from SQL
    studyIDs_in_SQL = get_studyIDs_SQL(phenotype=phenotype, studyID=studyID)

    if studyID == None:
        diff = set(studyIDs_on_Server).difference(set(studyIDs_in_SQL))
        if len(diff) > 0:
            print('List of StudyIDs that should not have completed {0}.\nCheck the Individual Checklist and that the StudyID is spelled correctly:\n'.format(phenotype))
            for file in diff:
               print(file, folder_paths[file] )
        else:
            print('All files are spelled correct!')
    else:
        
        if studyID not in studyIDs_on_Server and studyID in studyIDs_in_SQL:
            print('StudyID: {0} is a valid StudyID, but DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
        elif studyID in studyIDs_on_Server and studyID not in studyIDs_in_SQL:
            print('StudyID: {0} is NOT a valid StudyID, but DOES exist in the {1} phenotype folder'.format(studyID, phenotype))
            print(studyID, folder_paths[studyID])
        elif studyID not in studyIDs_on_Server and studyID not in studyIDs_in_SQL:
            print('StudyID: {0} is NOT a valid StudyID and DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
        else:
            print('StudyID: {0} is spelled correctly on server!'.format(studyID))
            print(studyID, folder_paths[studyID])
    print()

def check_contents():
    contents_dic = {'HandScan':{'.tif':1, '.tps':2},
                    'PalateVideo':{'.mov':1},
                    'Photos3D':{'.tsb':2, '_Clean.bmp':1, '_Clean.gif':1, '_Clean.mtl':1, '_Clean.obj':1, '_Belgium.obj':1, '_Clean_Standard.pdf':1, '_Clean_Standard.tsb':1, '_Clean_Standard.txt':1 }
                    }

def get_submit(drive, phenotype, studyID=None):
    check_folder(drive, phenotype, studyID)
    check_spelling(drive, phenotype, studyID)

drive = 'P:' 
phenotype = 'IntraoralPhotos'
get_submit(drive, phenotype, studyID=None)

#def main():

    #phenotype_list = ['LipUltrasound', 'LipPhotos', 'LHFPhoto', 'IntraoralPhotos', 'PalateVideo', 
    #                  'Photos3D', 'DentalImpression', 'HandScan', 'IDVideo', 'STVideo', 'SPVideo']


###### Test check_in_correct_folder:
    #drive = 'P:' 
    #phenotype = 'IntraoralPhotos'
    #check_folder(drive, phenotype)
    #check_folder(drive, phenotype, studyID='LC10037')

############


###### Test check_spelling:
    #drive = 'R:'
    #phenotype = 'LipPhotos'
    #studyID = 'PH17400'
    #check_spelling(drive, phenotype)
     
############
 

#if __name__ == '__main__': 
#    main()


#root = Tk()
#root.geometry('450x450+500+200')

#studyID = StringVar()
#drive_name = StringVar()
#phenotype = StringVar()
#output = StringVar()

#frame = Frame(root)
#fromLabel = Label(frame, text='StudyID:')
#fromLabel.pack(side=LEFT)
#fromEntry = Entry(frame, textvariable=studyID, width=9)
#fromEntry.pack(side=LEFT)
#frame.pack()

#frame = Frame(root)
#label = Label(frame, text='Drive')
#drive = ['', 'R:', 'P:']
#drive_dd = ttk.OptionMenu(frame, drive_name, *drive)
#drive_name.set('R:')
#label.pack(side="left")
#drive_dd.pack(side="left")
#frame.pack()

#frame = Frame(root)
#label = Label(frame, text='Phenotype')
#phenotype_labels = ['', 'LipUltrasound', 'LipPhotos', 'LHFPhoto', 'IntraoralPhotos', 'PalateVideo', 'Photos3D', 'DentalImpression', 'HandScan', 'SpeechVideos']
#phenotype_dd = ttk.OptionMenu(frame, phenotype, *phenotype_labels)
#phenotype.set('                   ')
#label.pack(side="left")
#phenotype_dd.pack(side="left")
#frame.pack()

## Submit button
#frame = Frame()
#submitButton = ttk.Button(frame, text='Submit', command=get_submit, width=10)
#submitButton.pack()
#frame.pack()

#frame = Frame(root)
#label = Label(frame, text='Output')
#output = Text(frame, width=50, height=50)
#output.pack()
#frame.pack()

#root.mainloop()
