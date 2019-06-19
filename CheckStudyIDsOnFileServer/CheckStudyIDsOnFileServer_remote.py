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


import pypyodbc
import os
import re
import sys


def sql_connection():
    """Creates a SQL connection"""
    connection_string = ('Driver={SQL Server};' 
                         #'Server=DESKTOP-JBRHK3M;'

			             'Database=OFC2;' 
			             'Trusted_Connection=Yes')
    connection = pypyodbc.connect(connection_string)
    return connection


def oom_studyIDs():
    """Finds completed OOM StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [LipUltrasound] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:][0])
    return studyIDs_in_SQl_list



def lipPhotos_studyIDs():
    """Finds completed LipPhotos StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [LipPhotos] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list


def lhfPhoto_studyIDs():
    """Finds completed LHFPhoto StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [LHFPhoto] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list


def iop_studyIDs():
    """Finds completed IOP StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [IntraoralPhotos] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list

def palateVideo_studyIDs():
    """Finds completed PalateVideo StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [PalateVideo] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list

def photos3D_studyIDs():
    """Finds completed Photos3D StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [Photos3D] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list

def dentalImpression_studyIDs():
    """Finds completed DentalImpression StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [DentalImpression] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list


def handScan_studyIDs():
    """Finds completed HandScan StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [HandScan] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list

def idVideo_studyIDs():
    """Finds completed IDVideo StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [IDVideo] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list

def stVideo_studyIDs():
    """Finds completed STVideo StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [STVideo] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list

def spVideo_studyIDs():
    """Finds completed SPVideo StudyIDs"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT 
     [StudyID]
       
    FROM IndividualChecklistExported
    WHERE [SPVideo] = 1
    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0:])
    return studyIDs_in_SQl_list


def ooms_on_Server():
    """Finds StudyIDs used on file server"""
    folder_list = []
    
    folder = r'R:\OFC2\PhenotypeRating\OOM'
    for root, dirs, files in os.walk(folder):
        indiv_folder = {}
        file_list = []
        for file in files:
            pattern = r'[a-zA-Z]{2}[0-9]{5}'
            match = re.search(pattern, file)
            if match:
                file = file[0:2].upper() + file[2:]
                file_list.append(file)
        indiv_folder = {match[0]:file_list}
        folder_list.append(indiv_folder)
        
    return folder_list

def check_in_correct_folder(path):
    wrong_folder = []
    for root, dirs, files in os.walk(path):
        for file in files:
            print(file, end='\r')
            match = re.search("[A-Za-z]{2}[0-9]{5}", file)
            if match and ('Library' in root or '1ToProcess' in root) and ('Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                if file[match.start():match.end()] not in root:
                   wrong_folder.append(os.path.join(root, file))
    return wrong_folder



def check_spelling(path, studyIDs):
    mispelled_IDs = []
    for root, dirs, files in os.walk(path):
        for file in files:
            print(file, end='\r')
            match = re.search("[A-Za-z]{2}[0-9]{5}", file)
            if match and ('Library' in root or '1ToProcess' in root) and ('Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):              
                if file[match.start():match.end()] not in studyIDs:
                    mispelled_IDs.append(os.path.join(root, file))
    return mispelled_IDs

def main():
    studyID_list = studyIDs_in_SQL()
    for studyID in studyID_list:
        print(studyID)

if __name__ == '__main__': 
    main()
