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


def get_file_paths():
    phenotype_paths = {'LipUltrasound':r'R:\OFC2\PhenotypeRating\OOM', 
                    'LipPhotos':r'R:\OFC2\PhenotypeRating\LipPhotos',
                    'LHFPhoto':r'R:\OFC2\PhenotypeRating\WoundHealingPhotos',
                    'IntraoralPhotos':r'R:\OFC2\PhenotypeRating\IntraOralPhotos',
                    'PalateVideo':r'R:\OFC2\PhenotypeRating\PalateVideos',
                    'Photos3D':r'R:\OFC2\PhenotypeRating\3DImages',
                    'DentalImpression':'R:\OFC2\PhenotypeRating\DentalCast',
                    'HandScan':r'R:\OFC2\PhenotypeRating\Hand Scan',
                    'SpeechVideos':r'R:\OFC2\PhenotypeRating\SpeechVideos'
                    }
    return phenotype_paths


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


def get_studyIDs_Server(phenotype, studyID = None):
    """Finds StudyIDs used on file server"""
    print('\nSearching file server in the {0} phenotype folder for StudyIDs'.format(phenotype))
 
    phenotype_paths = get_file_paths()

    path = phenotype_paths[phenotype]
    studyID_list = []
    if studyID == None:
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                match = re.search("[A-Za-z]{2}[0-9]{5}", dir)    
                if match and ('Library' in root or '1ToProcess' in root) and ('Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                    print('StudyID:', dir[match.start():match.end()], end='\r')
                    studyID_list.append(dir[match.start():match.end()]) 
    else:
        for root, dirs, files in os.walk(path):
            if studyID in dirs:
                for dir in dirs:
                    match = re.search("[A-Za-z]{2}[0-9]{5}", dir)    
                    if match and ('Library' in root or '1ToProcess' in root) and ('Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                        print('StudyID:', dir[match.start():match.end()], end='\r')
                        studyID_list.append(dir[match.start():match.end()])
    print('StudyID: Done!     ')
    print()
    return studyID_list


def check_folder(phenotype, studyID = None):
    """Check if file is in the correct folder"""
    phenotype_paths = get_file_paths()
    path = phenotype_paths[phenotype]

    print('************************************\nFolder Check for {0}\n************************************'.format(phenotype))
    wrong_folder = []

    if studyID == None:
        for root, dirs, files in os.walk(path):
            for file in files:
                match = re.search("[A-Za-z]{2}[0-9]{5}", file) 
                if match and ('Library' in root or '1ToProcess' in root) and ('Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                    print('Checking files for:', file[match.start():match.end()], end='\r')
                    if file[match.start():match.end()] not in root:
                       wrong_folder.append(os.path.join(root, file))
    else:
        for root, dirs, files in os.walk(path):
            if studyID in root:
                for file in files:
                    match = re.search("[A-Za-z]{2}[0-9]{5}", file) 
                    if match and ('Library' in root or '1ToProcess' in root) and ('Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
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

def check_spelling(phenotype, studyID = None):
    """Check if file has the correct spelling for a StudyID"""
    diff = []
    studyIDs_on_Server = get_studyIDs_Server(phenotype=phenotype, studyID=studyID)
    studyIDs_in_SQL = get_studyIDs_SQL(phenotype=phenotype, studyID=studyID)

    print('************************************\nSpelling Check\n************************************')
    if studyID == None:
        diff = set(studyIDs_on_Server).difference(set(studyIDs_in_SQL))
        if len(diff) > 0:
            print('List of StudyIDs that should not have completed {0}.\nCheck the Individual Checklist and that the StudyID is spelled correctly:\n'.format(phenotype))
            for file in diff:
               print(file)
        else:
            print('All files are spelled correct!')
    else:
        
        if studyID not in studyIDs_on_Server and studyID in studyIDs_in_SQL:
            print('StudyID: {0} is a valid StudyID, but does not exist in the {1} phenotype folder'.format(studyID, phenotype))
        elif studyID in studyIDs_on_Server and studyID not in studyIDs_in_SQL:
            print('StudyID: {0} is NOT a valid StudyID, but DOES exist in the {1} phenotype folder'.format(studyID, phenotype))
        elif studyID not in studyIDs_on_Server and studyID not in studyIDs_in_SQL:
            print('StudyID: {0} is NOT a valid StudyID and DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
        else:
            print('StudyID: {0} is spelled correctly on server!'.format(studyID))
    print()

def check_contents():
    contents_dic = {'HandScan':{'.tif':1, '.tps':2},
                    'PalateVideo':{'.mov':1}
                    
                    }


def main():

    #phenotype_list = ['LipUltrasound', 'LipPhotos', 'LHFPhoto', 'IntraoralPhotos', 'PalateVideo', 
    #                  'Photos3D', 'DentalImpression', 'HandScan', 'IDVideo', 'STVideo', 'SPVideo']


    ###### Test check_in_correct_folder:
      
    #check_folder('LipPhotos')
    #check_folder('LipPhotos', studyID='LC10037')

    ############


    ###### Test check_spelling:

    #phenotype = 'IntraoralPhotos'
    #studyID = 'PH17400'
    #check_spelling(phenotype)
     
    ############
    pass

if __name__ == '__main__': 
    main()
