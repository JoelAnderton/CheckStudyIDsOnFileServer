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
#       - 9/9/2019
#           - Excluded LipPhots because unusable, not received, or lip pits.
#              
#####################################################################################################################################
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile 
import pypyodbc
import os
import re
import sys
import csv
import re
import datetime
import itertools


def sql_connection():
    """Creates a SQL connection"""
    connection_string = ('Driver={SQL Server};' 
                         'Server= '
			             'Database=OFC2;' 
			             'Trusted_Connection=Yes')
    connection = pypyodbc.connect(connection_string)
    return connection


def sql_connection2():
    """Creates a SQL connection"""
    connection_string = ('Driver={SQL Server};' 
                         'Server= '
			             'Database=OFC Ratings;' 
			             'Trusted_Connection=Yes')
    connection = pypyodbc.connect(connection_string)
    return connection


def get_lip_to_process_studyIDs_SQL(phenotype, studyID=''):
    """Finds completed StudyIDs in SQL"""
    text.config(state='normal')
    #print('Searching SQL for Lip Photo StudyIDs To Process')
    studyID_list = []
    studyID_list.append(studyID)
    connection = sql_connection2()
    cur = connection.cursor()

    if studyID == '': # if not given an individual StudyID
        sqlcode = ('''  
        SELECT 
         [StudyID]
        ,[LipPhotosArchived]
        ,[LipPhotosProcessed]

        FROM [OFC Ratings].[dbo].[PhenotypeChecklist_LipPhotos_VW]
        WHERE [LipPhotosArchived] = 1 and ([LipPhotosProcessed] =0 or [LipPhotosProcessed] is null)
        ''')
        cur.execute(sqlcode)
    else: # if given an individual StudyID
        sqlcode = ('''  
        SELECT 
         [StudyID]
        ,[LipPhotosArchived]
        ,[LipPhotosProcessed]

        FROM [OFC Ratings].[dbo].[PhenotypeChecklist_LipPhotos_VW]
        WHERE [LipPhotosArchived] = 1 and ([LipPhotosProcessed] =0 or [LipPhotosProcessed] is null) AND [StudyID] = ?
        ''')
        cur.execute(sqlcode, studyID_list)

    studyIDs_in_SQl_toProcess = []
    text.delete('5.0','end')
    text.insert(INSERT, '\nGathering StudyIDs from SQL:\n')
    for row in cur.fetchall():
        #print(row)
        text.insert(INSERT, '\nStudyID: {0}'.format(row[0:][0]))
        text.see(END)
        text.update()
        text.delete('6.0','end')
        #print('StudyID: {0}'.format(row[0:][0]), end='\r')
        studyIDs_in_SQl_toProcess.append(row)
    text.delete('6.0','end')
    text.insert('6.0', '\nStudyID: Done!       ')
    #print('StudyID: Done!     ')
    #print()
    return studyIDs_in_SQl_toProcess


def get_IDs_to_exclude(phenotype, studyID=''):
    """Finds StudyIDs in SQL to exclude from report because unusable, not received, or lip pits"""
    studyID_list = []
    studyID_list.append(studyID)
    connection = sql_connection2()
    cur = connection.cursor()

    sql_code_dic = {'LipUltrasound':'SELECT [StudyID], [LipUltrasound], [OOMProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_OOM_VW] WHERE [LipUltrasound] = 1 and [OOMProcessed] = 0', 
                    'LipPhotos':'SELECT  [StudyID], [LipPhotos], [LipPhotosArchived], [LipPhotosProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_LipPhotos_VW] WHERE (LipPhotos=1 AND [LipPhotosReceived]=1 AND  [LipPhotosArchived]=0 AND LipPhotosProcessed=0) OR   (LipPhotos=1 AND LipPhotosReceived IS NULL AND LipPhotosArchived IS NULL AND LipPhotosReceived IS NULL) OR (LipPhotos=1 AND LipPits_=1 AND [LipPit_YesNo]=1)',
                    'LHFPhoto': 'SELECT [StudyID], [LHFPhoto], [WoundHealingProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_LHF Photo_VW]  WHERE [LHFPhoto] = 1 AND [WoundHealingProcessed] = 0',
                    'IntraoralPhotos':'SELECT [StudyID], [IntraoralPhotos], [IntraOralProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_IOP_VW] WHERE [IntraoralPhotos] =1 AND [IntraOralProcessed]=0',
                    'PalateVideo':'SELECT [StudyID], [PalateVideo], [PalateVideosProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_PalateVideo_VW] WHERE [PalateVideo] =1 AND [PalateVideosProcessed]=0',
                    'Photos3D':'SELECT [StudyID], [Photos3D], [Photos3DProcessed]  FROM [OFC Ratings].[dbo].[PhenotypeChecklist_3DPhoto_VW]  WHERE [Photos3D] =1 AND [Photos3DProcessed] =0',
                    'DentalImpression':'SELECT [StudyID], [DentalImpression], [DentalCastProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_DentalImpression_VW] WHERE [DentalImpression] = 1 AND [DentalCastProcessed] = 0',
                    'HandScan':'SELECT  [StudyID], [HandScan], [HandScanProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_HandScan_VW] WHERE [HandScan] =1 AND [HandScanProcessed] = 0',
                    'SpeechVideos':'SELECT [StudyID], [SpeechVideos], [SpeechVideosProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_SpeechVideo_VW]  WHERE [SpeechVideos] =1 AND [SpeechVideosProcessed] =0'
        }

    sql_code_dic_with_StudyID = {'LipUltrasound':'SELECT [StudyID], [LipUltrasound], [OOMProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_OOM_VW] WHERE [LipUltrasound] = 1 and [OOMProcessed] = 0 AND [StudyID] =?',
                    'LipPhotos':'SELECT  [StudyID], [LipPhotos], [LipPhotosArchived], [LipPhotosProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_LipPhotos_VW] WHERE (LipPhotos=1 AND [LipPhotosReceived]=1 AND [LipPhotosArchived]=0 AND LipPhotosProcessed=0) OR   (LipPhotos=1 AND LipPhotosReceived IS NULL AND LipPhotosArchived IS NULL AND LipPhotosReceived IS NULL) OR (LipPhotos=1 AND LipPits_=1 AND [LipPit_YesNo]=1) AND [StudyID] =?',
                    'LHFPhoto': 'SELECT [StudyID], [LHFPhoto], [WoundHealingProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_LHF Photo_VW]  WHERE [LHFPhoto] = 1 AND [WoundHealingProcessed] = 0 AND [StudyID] =?',
                    'IntraoralPhotos':'SELECT [StudyID], [IntraoralPhotos], [IntraOralProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_IOP_VW] WHERE [IntraoralPhotos] =1 AND [IntraOralProcessed]=0 AND [StudyID] =?',
                    'PalateVideo':'SELECT [StudyID], [PalateVideo], [PalateVideosProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_PalateVideo_VW] WHERE [PalateVideo] =1 AND [PalateVideosProcessed]=0 AND [StudyID] =?',
                    'Photos3D':'SELECT [StudyID], [Photos3D], [Photos3DProcessed]  FROM [OFC Ratings].[dbo].[PhenotypeChecklist_3DPhoto_VW]  WHERE [Photos3D] =1 AND [Photos3DProcessed] =0 AND [StudyID] =?',
                    'DentalImpression':'SELECT [StudyID], [DentalImpression], [DentalCastProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_DentalImpression_VW] WHERE [DentalImpression] = 1 AND [DentalCastProcessed] = 0 AND [StudyID] =?',
                    'HandScan':'SELECT  [StudyID], [HandScan], [HandScanProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_HandScan_VW] WHERE [HandScan] =1 AND [HandScanProcessed] = 0 AND [StudyID] =?',
                    'SpeechVideos':'SELECT [StudyID], [SpeechVideos], [SpeechVideosProcessed] FROM [OFC Ratings].[dbo].[PhenotypeChecklist_SpeechVideo_VW]  WHERE [SpeechVideos] =1 AND [SpeechVideosProcessed] =0 AND [StudyID] =?'
        }

    if studyID == '': # if not given an individual StudyID
        sqlcode = (sql_code_dic[phenotype])
        cur.execute(sqlcode)
    else: # if given an individual StudyID
        sqlcode = (sql_code_dic_with_StudyID[phenotype])
        cur.execute(sqlcode, studyID_list)

    IDs_to_exclude = []
    for row in cur.fetchall():
        IDs_to_exclude.append(row[0])
    return IDs_to_exclude


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
                          }
                     }
    #print(phenotype_paths[drive][phenotype])
    return phenotype_paths[drive][phenotype]


def get_studyIDs_SQL(phenotype, studyID=''):
    """Finds completed StudyIDs in SQL"""
    text.config(state='normal')
    #print('Searching SQL for StudyIDs')
    studyID_list = []
    studyID_list.append(studyID)
    connection = sql_connection()
    cur = connection.cursor()

    if studyID == '': # if not given an individual StudyID
        sqlcode = ('''  
        SELECT 
         [StudyID]
        ,[LipUltrasound]
	    ,[LipPhotos]
        ,[LHFPhoto]
        ,[IntraoralPhotos]
        ,[PalateVideo]
        ,[Photos3D]
        ,[DentalImpression]
	    ,[HandScan]
        ,[SpeechVideos]
        ,[IDVideo]
        ,[STVideo]
        ,[SPVideo]
        ,[CameraType]

        FROM IndividualChecklistExported
        WHERE {0} = 1
        '''.format(phenotype))
        cur.execute(sqlcode)
    else: # if given an individual StudyID
        sqlcode = ('''  
        SELECT 
         [StudyID]
        ,[LipUltrasound]
	    ,[LipPhotos]
        ,[LHFPhoto]
        ,[IntraoralPhotos]
        ,[PalateVideo]
        ,[Photos3D]
        ,[DentalImpression]
	    ,[HandScan]
        ,[SpeechVideos]
        ,[IDVideo]
        ,[STVideo]
        ,[SPVideo]
        ,[CameraType]
       
        FROM IndividualChecklistExported
        WHERE {0} = 1 AND [StudyID] = ?
        '''.format(phenotype))
        cur.execute(sqlcode, studyID_list)

    studyIDs_in_SQl_list = []
    text.delete('5.0','end')
    text.insert(INSERT, '\nGathering StudyIDs from SQL:\n')
    
    for row in cur.fetchall():
        #print(row)
        text.insert(INSERT, '\nStudyID: {0}'.format(row[0:][0]))
        text.see(END)
        text.update()
        text.delete('6.0','end')
        #print('StudyID: {0}'.format(row[0:][0]), end='\r')
        if phenotype not in ('Photos3D', 'SpeechVideos') :  # if phenotype = Photos3D we need the whole row of information because of the camera type...used later.
            studyIDs_in_SQl_list.append(row[0])
        else:
            studyIDs_in_SQl_list.append(row)
    text.delete('6.0','end')
    text.insert('6.0', '\nStudyID: Done!       ')
    #print('StudyID: Done!     ')
    #print()
    return studyIDs_in_SQl_list


def get_studyIDs_Server(drive, phenotype, studyID = ''):
    """Finds StudyIDs used on file server"""
    #print('Searching file server in the {0} phenotype folder for StudyIDs\n'.format(phenotype))
    path = get_file_paths(drive, phenotype)
    text.insert(INSERT, 'Searching file server in the {0} phenotype folder for StudyIDs\n'.format(phenotype))
    studyID_list = []
    if studyID == '':
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                match = re.search("[A-Za-z]{2}[0-9]{5}", dir)    
                if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                    text.insert('6.0', '\nStudyID: {0}\n'.format(dir[match.start():match.end()]))
                    text.see(END)
                    text.update()
                    text.delete('6.0','end')
                    #print('StudyID:', dir[match.start():match.end()], end='\r')
                    studyID_list.append({dir[match.start():match.end()]:os.path.join(root, dir[match.start():match.end()])}) 
    else:
        for root, dirs, files in os.walk(path):
            if studyID in dirs:
                for dir in dirs:
                    match = re.search("[A-Za-z]{2}[0-9]{5}", dir)    
                    if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                        text.insert('6.0', '\nStudyID: {0}\n'.format(dir[match.start():match.end()]))
                        text.see(END)
                        text.update()
                        text.delete('6.0','end')
                        #print('StudyID:', dir[match.start():match.end()], end='\r')
                        studyID_list.append({dir[match.start():match.end()]:os.path.join(root, dir[match.start():match.end()])})
    text.delete('6.0','end')
    #text.insert('5.0', 'StudyID: Done!            ')
    #print('StudyID: Done!     ')
    #print()
    return studyID_list


def check_folder(drive, phenotype, studyID = ''):
    """Check if file is in the correct folder"""
    path = get_file_paths(drive, phenotype)

    text.config(state='normal')
    text.delete('1.0', 'end')
    text.insert(INSERT, '**************************************************************************\nFolder Check for {0}: {1}\nCheck that the files are in the correct folders\n**************************************************************************\n'.format(phenotype, path))
    text.see(END)
    text.update()
    #print('****************************************************************\nFiles in Correct Folders Check for: {0}\n****************************************************************'.format(phenotype))
        
    wrong_folder = []

    if studyID == '':
        for root, dirs, files in os.walk(path):
            for file in files:
                
                match = re.search("[A-Za-z]{2}[0-9]{5}", file) 
                if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 
                              'Pittsburgh' in root or 'Puerto Rico' in root) and (not 'Logs' in root and not 'AhmedMamdouh' in root and not 'SteveMiller' in root and not 'DentalScansBelgium2019.4.24' in root and not 'Raw' in root):                
                    text.delete(5.0, 'end')
                    text.insert(INSERT, '\nChecking folder: {0}'.format(file[match.start():match.end()]))
                    text.see(END)
                    text.update()
                    #print('Checking files for:', file[match.start():match.end()], end='\r')
                    if file[match.start():match.end()] not in root:
                       wrong_folder.append(os.path.join(root, file))
    else:
        for root, dirs, files in os.walk(path):
            if studyID in root:
                for file in files:
                    match = re.search("[A-Za-z]{2}[0-9]{5}", file) 
                    if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 
                                  'Pittsburgh' in root or 'Puerto Rico' in root) and (not 'Logs' in root and not 'AhmedMamdouh' in root and not 'SteveMiller' in root and not 'DentalScansBelgium2019.4' in root): 
                        text.delete('5.0','end')
                        text.insert(INSERT, '\nChecking folder: {0}'.format(file[match.start():match.end()]))
                        text.see(END)
                        text.update()
                        #print('Checking files for:', file[match.start():match.end()], end='\r')
                        if file[match.start():match.end()] not in root:
                           wrong_folder.append(os.path.join(root, file))

 

    if len(wrong_folder) >0:
        text.delete(5.0, 'end')
        text.insert(INSERT, '\nCheck that the file is in the correct folder for the following:\n')
        text.see(END)
        text.update()
        #print('Check that the file is in the correct folder for the following:')

        cases = []
        position_list = []
        for num, file in enumerate(wrong_folder):
            match = re.findall("[A-Za-z]{2}[0-9]{5}", file)
            position = re.search("[A-Za-z]{2}[0-9]{5}", file)
            match = list(set(match)) # to convert it to a set and then back to to a list to remove any possible dups 
            cases.append(match)
            position_list.append(position.start())
            text.insert(INSERT,'{0}\n'.format(file)) 
        
        #for i in cases:
        #    print(i)

        diff_list = []
        for x, y in cases:
            diffs = [i for i in range(len(x)) if x[i] != y[i]]
            diff_list.append(diffs)

        line = 6
        for diffs, position in zip(diff_list, position_list):
                #print(diffs, position)
                for diff in diffs:
                    text.tag_add('diff{0}{1}'.format(line, diff + position), '{0}.{1}'.format(line, diff + position), '{0}.{1}'.format(line, diff + position + 1))
                    text.tag_config('diff{0}{1}'.format(line, diff + position), background='red')
                    if phenotype == 'Photos3D' and 'Faces Cleaned' in text.get('{0}.0'.format(line), "{0}.end".format(line)):
                        text.tag_add('diff2{0}{1}'.format(line, diff + position), '{0}.{1}'.format(line, diff + position + 14), '{0}.{1}'.format(line, diff + position + 15))
                        text.tag_config('diff2{0}{1}'.format(line, diff + position), background='light sky blue')

                    elif phenotype == 'Photos3D' and 'Landmarks' in text.get('{0}.0'.format(line), "{0}.end".format(line)):
                        text.tag_add('diff2{0}{1}'.format(line, diff + position), '{0}.{1}'.format(line, diff + position + 18), '{0}.{1}'.format(line, diff + position + 19))
                        text.tag_config('diff2{0}{1}'.format(line, diff + position), background='light sky blue')

                    elif phenotype == 'Photos3D' and 'Images' in text.get('{0}.0'.format(line), "{0}.end".format(line)):
                        text.tag_add('diff2{0}{1}'.format(line, diff + position), '{0}.{1}'.format(line, diff + position + 15), '{0}.{1}'.format(line, diff + position + 16))
                        text.tag_config('diff2{0}{1}'.format(line, diff + position), background='light sky blue')

                    elif phenotype == 'LipPhotos' and ('UL_' in text.get('{0}.0'.format(line), "{0}.end".format(line)) or 'LL_' in text.get('{0}.0'.format(line), "{0}.end".format(line))):
                        text.tag_add('diff2{0}{1}'.format(line, diff + position), '{0}.{1}'.format(line, diff + position + 11), '{0}.{1}'.format(line, diff + position + 12))
                        text.tag_config('diff2{0}{1}'.format(line, diff + position), background='light sky blue')

                    else:
                        text.tag_add('diff2{0}{1}'.format(line, diff + position), '{0}.{1}'.format(line, diff + position + 8), '{0}.{1}'.format(line, diff + position + 9))
                        text.tag_config('diff2{0}{1}'.format(line, diff + position), background='light sky blue')
                line += 1
    else:
        text.delete(5.0, 'end')
        text.insert(INSERT, '\nAll files are in their correct folders!')
        text.see(END)
        text.update()
        #print('All files are in their correct folders!')
    text.configure(state='disabled')


def check_spelling(drive, phenotype, studyID = ''):
    """Check if folder has the correct spelling for a StudyID"""
    path = get_file_paths(drive, phenotype)
    text.config(state='normal')
    text.delete('1.0', 'end')
    text.insert(INSERT, '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\nSpelling Check for {0}: {1}\nCheck if folder has the correct spelling for a StudyID\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'.format(phenotype, path))
    text.see(END)
    text.update()
    #print('************************************\nSpelling Check\n************************************')
    diff = []
    studyIDs_and_paths = get_studyIDs_Server(drive=drive, phenotype=phenotype, studyID=studyID)

    # Extracts folders and folder paths:
    studyIDs_on_Server = []
    folder_paths = {}
    for folders in studyIDs_and_paths:
        for folder, path in folders.items():
            studyIDs_on_Server.append(folder)
            folder_paths.update({folder : path})

    # Gets StudyIDs from SQL
    studyIDs_in_SQL = get_studyIDs_SQL(phenotype=phenotype, studyID=studyID)
    only_StudyIDs = []
    for row in studyIDs_in_SQL:   # get only the StudyIDs and add them to the only_StudyIDs list
        only_StudyIDs.append(row[0:][0])
    
    #print(only_StudyIDs)

    if studyID == '':
        diff = set(studyIDs_on_Server).difference(set(only_StudyIDs))
        if len(diff) > 0:
            text.delete('5.0', 'end')
            text.insert('5.0', '\nCheck the Individual Checklist and that the StudyID is spelled correctly:\n'.format(phenotype))
            text.see(END)
            text.update()
            #print('List of StudyIDs that should not have completed {0}.\nCheck the Individual Checklist and that the StudyID is spelled correctly:\n'.format(phenotype))
            for file in diff:
               text.insert(INSERT,'{0} : {1}\n'.format(file,folder_paths[file] ))
               text.see(END)
               text.update()
               #print(file, folder_paths[file] )
        else:
            text.insert(INSERT, '\nAll folders are spelled correctly!')
            text.see(END)
            text.update()
            #print('All files are spelled correct!')
    else:
        
        if studyID not in studyIDs_on_Server and studyID in only_StudyIDs:
            text.delete(6.0, 'end')
            text.insert(INSERT, '\nStudyID: {0} is a valid StudyID, but DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
            text.see(END)
            text.update()
            #print('StudyID: {0} is a valid StudyID, but DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
        elif studyID in studyIDs_on_Server and studyID not in only_StudyIDs:
            text.delete(6.0, 'end')
            text.insert(INSERT, '\nStudyID: {0} is a valid StudyID, but DOES exist in the {1} phenotype folder'.format(studyID, phenotype))
            text.see(END)
            text.update()
            #print('StudyID: {0} is NOT a valid StudyID, but DOES exist in the {1} phenotype folder'.format(studyID, phenotype))
            #print(studyID, folder_paths[studyID])
        elif studyID not in studyIDs_on_Server and studyID not in only_StudyIDs:
            text.delete(6.0, 'end')
            text.insert(INSERT, '\nStudyID: {0} is NOT a valid StudyID and DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
            text.see(END)
            text.update()
            #print('StudyID: {0} is NOT a valid StudyID and DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
        else:
            text.delete(6.0, 'end')
            text.insert(INSERT, '\nStudyID: {0} is spelled correctly on server!'.format(studyID))
            text.see(END)
            text.update()
            #print('StudyID: {0} is spelled correctly on server!'.format(studyID))
            #print(studyID, folder_paths[studyID])

    text.configure(state='disabled')


def check_contents(drive, phenotype, studyID=''):
    '''Check that the subject(s) have all the correct files on the file server if SQL says they completed them'''
    path = get_file_paths(drive, phenotype)

    text.config(state='normal')
    text.delete('1.0', 'end')
    text.insert(INSERT, '==========================================================================\nCheck Contents for {0}: {1}\nCheck that the subject has all the correct files they are supposed to have.\n==========================================================================\n'.format(phenotype, path))
    text.see(END)
    text.update()

    studyIDs_in_SQL = get_studyIDs_SQL(phenotype=phenotype, studyID=studyID)
    # find subjects that we can expect to exclude from the report because unusable files.
    exclude_list = get_IDs_to_exclude(phenotype=phenotype, studyID=studyID)
    if phenotype not in ('Photos3D', 'SpeechVideos'):
        # remove subjects we know will not have files because they are unusuable.   Photos3D has it's own process to remove excluded subjects
        studyIDs_in_SQL = sorted(list(set(studyIDs_in_SQL).difference(set(exclude_list))))
    
    contents_dic = {'R:': 
                    {'LipUltrasound':['[A-Za-z]{2}[0-9]{5}.*\.[Mm][Pp][4]'],

                    'LipPhotos':['[A-Za-z]{2}[0-9]{5}.*LIL.*\.[Jj][Pp][Gg]',
                                 '[A-Za-z]{2}[0-9]{5}[Pp][0-9]\.[Jj][Pp][Gg]',
                                 'LL_[A-Za-z]{2}[0-9]{5}_[Ii][Nn][Vv]\.[Jj][Pp][Gg]',
                                 'LL_[A-Za-z]{2}[0-9]{5}_[Nn][Oo][Rr]\.[Jj][Pp][Gg]',
                                 'LL_[A-Za-z]{2}[0-9]{5}_[Pp][Cc][Oo]\.[Jj][Pp][Gg]',
                                 'UL_[A-Za-z]{2}[0-9]{5}_[Ii][Nn][Vv]\.[Jj][Pp][Gg]',
                                 'UL_[A-Za-z]{2}[0-9]{5}_[Nn][Oo][Rr]\.[Jj][Pp][Gg]',
                                 'UL_[A-Za-z]{2}[0-9]{5}_[Pp][Cc][Oo]\.[Jj][Pp][Gg]'],

                    'LHFPhoto':['[A-Za-z]{2}[0-9]{5}.*\.[Jj][Pp][Gg]'],

                     'IntraoralPhotos':['[A-Za-z]{2}[0-9]{5}[Tt][0-9]{1,2}.[Jj][Pp][Gg]'],

                     'PalateVideo':['[A-Za-z]{2}[0-9]{5}PAL.*\.[Mm][Oo][Vv]'],

                     'Photos3D':['[A-Za-z]{2}[0-9]{5}.*\.[Tt][Ss][Bb]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean\.[Tt][Ss][Bb]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean\.[Oo][Bb][Jj]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean\.[Gg][Ii][Ff]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean\.[Mm][Tt][Ll]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean\.[Bb][Mm][Pp]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean_Belgium\.[Oo][Bb][Jj]',
                                 '[A-Za-z]{2}[0-9]{5}.*\.[Oo][Bb][Jj]',
                                 '[A-Za-z]{2}[0-9]{5}.*\.[Bb][Mm][Pp]',
                                 '[A-Za-z]{2}[0-9]{5}.*\.[Mm][Tt][Ll]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean_Standard\.[Tt][Ss][Bb]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean_Standard\.[Pp][Dd][Ff]',
                                 '[A-Za-z]{2}[0-9]{5}.*Clean_Standard\.[Tt][Xx][Tt]'
                                  ],

                     'DentalImpression':['[A-Za-z]{2}[0-9]{5}MAND\.[Ss][Tt][Ll]',
                                         '[A-Za-z]{2}[0-9]{5}MAX\.[Ss][Tt][Ll]'],

                     'HandScan':['[A-Za-z]{2}[0-9]{5}.*HSN.*\.[Tt][Ii][Tf]',
                                 '[A-Za-z]{2}[0-9]{5}.*HSN.*Left.*\.[Tt][Pp][Ss]', 
                                 '[A-Za-z]{2}[0-9]{5}.*HSN.*Right.*\.[Tt][Pp][Ss]'],

                     'SpeechVideos':['[A-Za-z]{2}[0-9]{5}.*ID.*\.[Mm][Oo][Vv]',
                                     '[A-Za-z]{2}[0-9]{5}.*ST.*\.[Mm][Oo][Vv]', 
                                     '[A-Za-z]{2}[0-9]{5}.*SP.*\.[Mm][Oo][Vv]']
                     },
                'P:': 
                    {'LipUltrasound':['[A-Za-z]{2}[0-9]{5}.*\.[Mm][Pp][4]'],

                     'LipPhotos':['[A-Za-z]{2}[0-9]{5}.*LIL.*\.[Jj][Pp][Gg]',
                                 '[A-Za-z]{2}[0-9]{5}[Pp][0-9]{1,2}\.[Jj][Pp][Gg]',
                                 'LL_[A-Za-z]{2}[0-9]{5}\.[Pp][Ss][Dd]',
                                 'UL_[A-Za-z]{2}[0-9]{5}\.[Pp][Ss][Dd]'],


                     'LHFPhoto':['[A-Za-z]{2}[0-9]{5}.*\.[Jj][Pp][Gg]'],

                     'IntraoralPhotos':['[A-Za-z]{2}[0-9]{5}t[0-9]{1,2}.[Jj][Pp][Gg]'],

                     'PalateVideo':['[A-Za-z]{2}[0-9]{5}PAL.*\.[Mm][Oo][Vv]'],

                     'DentalImpression':['[A-Za-z]{2}[0-9]{5}MAND\.[Ss][Tt][Ll]',
                                         '[A-Za-z]{2}[0-9]{5}MANDraw\.[Ss][Tt][Ll]',
                                         '[A-Za-z]{2}[0-9]{5}MAX\.[Ss][Tt][Ll]',
                                         '[A-Za-z]{2}[0-9]{5}MAXraw\.[Ss][Tt][Ll]'],

                     'HandScan':['[A-Za-z]{2}[0-9]{5}.*HSN.*\.[Tt][Ii][Tf]'],

                     'SpeechVideos':['[A-Za-z]{2}[0-9]{5}.*ID.*\.[Mm][Oo][Vv]',
                                     '[A-Za-z]{2}[0-9]{5}.*ST.*\.[Mm][Oo][Vv]', 
                                     '[A-Za-z]{2}[0-9]{5}.*SP.*\.[Mm][Oo][Vv]'],

                     'Photos3D':['[A-Za-z]{2}[0-9]{5}.*\.[Tt][Ss][Bb]',
                                 '[A-Za-z]{2}[0-9]{5}.*\.[Tt][Oo][Mm]'
                                  ]
                     }
                } 

    on_fileserver = [] # list of those that exist on fileserver
    should_have = [] # list of files they should have
    missing = [] # list of missing files

    text.delete('5.0','end')
    text.insert(INSERT, '\nSearching File Server for files\n')
      
    # Handles 'LipUltrasound', 'LHFPhoto', 'PalateVideo' Contents Check  both R: and P: drives  
    if phenotype in ['LipUltrasound', 'LHFPhoto', 'PalateVideo']: 
        if studyID == '':
            for root, dirs, files in os.walk(path):
                for file in files:
                    for pattern in contents_dic[drive][phenotype]:
                        match = re.findall(pattern, file)
                        if match:
                            study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                            #print('Appending', study_ID_in_file[0], file)                        
                            text.insert(INSERT, '\nFile: {0}\n'.format(file))
                            text.see(END)
                            text.update()
                            text.delete('6.0','end')
                            on_fileserver.append(study_ID_in_file[0])
        else:
            for root, dirs, files in os.walk(path):
                if studyID in root:
                    for file in files:
                        for pattern in contents_dic[drive][phenotype]:
                            match = re.findall(pattern, file)
                            if match:
                                study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                                #print('Appending', study_ID_in_file[0], file)                        
                                text.insert(INSERT, '\nFile: {0}\n'.format(file))
                                text.see(END)
                                text.update()
                                text.delete('6.0','end')
                                on_fileserver.append(study_ID_in_file[0])

        for studyID in studyIDs_in_SQL:
            should_have.append(studyID)

        # find only the subject's that are missing"
        missing = sorted(list(set(should_have).difference(set(on_fileserver))))
        
        text.delete('5.0','end')  
        text.insert(INSERT, '\nCheck the Individual Checklist and phenotype folder for the following:\n'.format(phenotype))
        if len(missing) >0:
            for studyID in missing:
                if phenotype == 'LipUltrasound':
                    file_extenstion = '.mp4'
                elif phenotype in 'LHFPhoto': 
                    file_extenstion = '.jpg'
                elif phenotype == 'PalateVideo':
                    file_extenstion = '.mov'
                else:
                    file_extenstion = 'some'

                text.insert(INSERT,'{0} is missing a {1} file\n'.format(studyID, file_extenstion))
                text.see(END)
                text.update()
                #print(studyID, 'is missing an .mp4 file')
            text.insert(INSERT,'Total number of files missing: {}'.format(len(missing)))
            #print('Total number of files missing: {}'.format(len(missing))) 
                    
        else:
            text.insert(INSERT, '\nAll subjects have the correct files!')
            text.see(END)
            text.update()
            #print('All subjects have the correct files!')

    # Handles IntraoralPhotos Contents Check  both R: and P: drives 
    elif  phenotype == 'IntraoralPhotos':
        if studyID == '':
            for root, dirs, files in os.walk(path):
                for file in files:
                    for pattern in contents_dic[drive][phenotype]:
                        match = re.findall(pattern, file)
                        if match:
                            #print('Appending', file)                        
                            text.insert(INSERT, '\nFile: {0}\n'.format(file))
                            text.see(END)
                            text.update()
                            text.delete('6.0','end')
                            on_fileserver.append(file)
        else:
            for root, dirs, files in os.walk(path):
                if studyID in root:
                    for file in files:
                        for pattern in contents_dic[drive][phenotype]:
                            match = re.findall(pattern, file)
                            if match:
                                #print('Appending', file)                        
                                text.insert(INSERT, '\nFile: {0}\n'.format(file))
                                text.see(END)
                                text.update()
                                text.delete('6.0','end')
                                on_fileserver.append(file)
    
        for studyID in studyIDs_in_SQL:
            for num in range(1, 8):
                should_have_IOP_file = '{0}t{1}.JPG'.format(studyID, num)
                should_have.append(should_have_IOP_file)
        
        # find only the subject's that are missing"
        missing = sorted(list(set(should_have).difference(set(on_fileserver))))

        text.delete('5.0','end')  
        text.insert(INSERT, '\nCheck the Individual Checklist and phenotype folder for the following:\n'.format(phenotype))
        if len(missing) >0:
            for studyID in missing:
                text.insert(INSERT,'{0} is missing\n'.format(studyID))
                text.see(END)
                text.update()
                #print(studyID, 'is missing')
            text.insert(INSERT,'Total number of files missing: {}'.format(len(missing)))
            #print('Total number of files missing: {}'.format(len(missing))) 
        else:
            text.insert(INSERT, '\nAll subjects have the correct files!')
            text.see(END)
            text.update()
            #print('All subjects have the correct files!')

    # Handles DentalImpression Contents Check  both R: and P: drives 
    elif phenotype == 'DentalImpression':
        if studyID == '':
            for root, dirs, files in os.walk(path):
                for file in files:
                    for pattern in contents_dic[drive][phenotype]:
                        match = re.findall(pattern, file)
                        if match:
                            #print('Appending', file)                        
                            text.insert(INSERT, '\nFile: {0}\n'.format(file))
                            text.see(END)
                            text.update()
                            text.delete('6.0','end')
                            on_fileserver.append(file)
        else:
            for root, dirs, files in os.walk(path):
                if studyID in root:
                    for file in files:
                        for pattern in contents_dic[drive][phenotype]:
                            match = re.findall(pattern, file)
                            if match:
                                #print('Appending', file)                        
                                text.insert(INSERT, '\nFile: {0}\n'.format(file))
                                text.see(END)
                                text.update()
                                text.delete('6.0','end')
                                on_fileserver.append(file)

        for studyID in studyIDs_in_SQL:
            should_have_MAND = '{}MAND.stl'.format(studyID)
            should_have.append(should_have_MAND)
            should_have_MAX = '{}MAX.stl'.format(studyID)
            should_have.append(should_have_MAX)
            if drive == 'P:':
                should_have_MANDraw = '{}MANDraw.stl'.format(studyID)
                should_have.append(should_have_MANDraw)
                should_have_MAXraw = '{}MAXraw.stl'.format(studyID)
                should_have.append(should_have_MAXraw)

        missing = sorted(list(set(should_have).difference(set(on_fileserver))))

        text.delete('5.0','end')  
        text.insert(INSERT, '\nCheck the Individual Checklist and phenotype folder for the following:\n'.format(phenotype))
        if len(missing) >0:
            for studyID in missing:
                text.insert(INSERT,'{0} is missing\n'.format(studyID))
                text.see(END)
                text.update()
                #print(studyID, 'is missing')
            text.insert(INSERT,'Total number of files missing: {}'.format(len(missing)))
            #print('Total number of files missing: {}'.format(len(missing)))
        else:
            text.insert(INSERT, '\nAll subjects have the correct files!')
            text.see(END)
            text.update()
            #print('All subjects have the correct files!') 

    # Handles HandScan Contents Check  both R: and P: drives 
    elif phenotype == 'HandScan':
        if studyID == '':
            for root, dirs, files in os.walk(path):
                for file in files:
                    for pattern in contents_dic[drive][phenotype]:
                        match = re.findall(pattern, file)
                        if match:
                            study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                            if '.tif' in file:
                                file = study_ID_in_file[0] + 'HSN.tif'
                            elif 'Left' in file:
                                file = study_ID_in_file[0] + 'HSN_Left.TPS'
                            elif 'Right' in file:
                                file = study_ID_in_file[0] + 'HSN_Right.TPS'
                            else:
                                pass
                            #print('Appending', file)                        
                            text.insert(INSERT, '\nFile: {0}\n'.format(file))
                            text.see(END)
                            text.update()
                            text.delete('5.0','end')
                            on_fileserver.append(file)
        else:
            for root, dirs, files in os.walk(path):
                if studyID in root:
                    for file in files:
                        for pattern in contents_dic[drive][phenotype]:
                            match = re.findall(pattern, file)
                            if match:
                                study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                                if '.tif' in file:
                                    file = study_ID_in_file[0] + 'HSN.tif'
                                elif 'Left' in file:
                                    file = study_ID_in_file[0] + 'HSN_Left.TPS'
                                elif 'Right' in file:
                                    file = study_ID_in_file[0] + 'HSN_Right.TPS'
                                else:
                                    pass
                                #print('Appending', file)                        
                                text.insert(INSERT, '\nFile: {0}\n'.format(file))
                                text.see(END)
                                text.update()
                                text.delete('5.0','end')
                                on_fileserver.append(file)

        for studyID in studyIDs_in_SQL:
            should_have_HSNtif = '{}HSN.tif'.format(studyID)
            should_have.append(should_have_HSNtif)
            if drive=='R:':
                should_have_HSNleft = '{}HSN_Left.TPS'.format(studyID) 
                should_have.append(should_have_HSNleft)
                should_have_HSNright = '{}HSN_Right.TPS'.format(studyID)
                should_have.append(should_have_HSNright)

        missing = sorted(list(set(should_have).difference(set(on_fileserver))))

        text.delete('5.0','end')  
        text.insert(INSERT, '\nCheck the Individual Checklist and phenotype folder for the following:\n'.format(phenotype))
        if len(missing) >0:
            for studyID in missing:
                text.insert(INSERT,'{0} is missing\n'.format(studyID))
                text.see(END)
                text.update()
                #print(studyID, 'is missing')
            text.insert(INSERT,'Total number of files missing: {}'.format(len(missing)))
            #print('Total number of files missing: {}'.format(len(missing))) 
        else:
            text.insert(INSERT, '\nAll subjects have the correct files!')
            text.see(END)
            text.update()

    # Handles SpeechVideos Contents Check  both R: and P: drives 
    elif phenotype == 'SpeechVideos':
        if studyID == '':
            for root, dirs, files in os.walk(path):
                for file in files:
                    for pattern in contents_dic[drive][phenotype]:
                        match = re.findall(pattern, file)
                        if match:
                            study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                            if 'ID' in file.upper():
                                file = study_ID_in_file[0] + '_ID.mov'
                            elif 'ST' in file.upper():
                                file = study_ID_in_file[0] + '_ST.mov'
                            elif 'SP' in file.upper():
                                file = study_ID_in_file[0] + '_SP.mov'
                            #print('Appending', file)                        
                            text.insert(INSERT, '\nFile: {0}\n'.format(file))
                            text.see(END)
                            text.update()
                            text.delete('5.0','end')
                            on_fileserver.append(file)
        else:
            for root, dirs, files in os.walk(path):
                if studyID in root:
                    for file in files:
                        for pattern in contents_dic[drive][phenotype]:
                            match = re.findall(pattern, file)
                            if match:
                                study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                                if 'ID' in file.upper():
                                    file = study_ID_in_file[0] + '_ID.mov'
                                elif 'ST' in file.upper():
                                    file = study_ID_in_file[0] + '_ST.mov'
                                elif 'SP' in file.upper():
                                    file = study_ID_in_file[0] + '_SP.mov'
                               #print('Appending', file)                        
                                text.insert(INSERT, '\nFile: {0}\n'.format(file))
                                text.see(END)
                                text.update()
                                text.delete('5.0','end')
                                on_fileserver.append(file)


        for studyID in studyIDs_in_SQL:
            #print(studyID)
            if studyID[0] in exclude_list:
                continue
            if studyID[10] == 1:
                should_have_ID = '{}_ID.mov'.format(studyID[0])
                should_have.append(should_have_ID)
            if studyID[11] == 1:
                should_have_ST = '{}_ST.mov'.format(studyID[0]) 
                should_have.append(should_have_ST)
            if studyID[12] == 1:
                should_have_SP = '{}_SP.mov'.format(studyID[0])
                should_have.append(should_have_SP)

        missing = sorted(list(set(should_have).difference(set(on_fileserver))))

        text.delete('5.0','end')  
        text.insert(INSERT, '\nCheck the Individual Checklist and phenotype folder for the following:\n'.format(phenotype))
        if len(missing) >0:
            for studyID in missing:
                text.insert(INSERT,'{0} is missing\n'.format(studyID))
                text.see(END)
                text.update()
                #print(studyID, 'is missing')
            text.insert(INSERT,'Total number of files missing: {}'.format(len(missing)))
            #print('Total number of files missing: {}'.format(len(missing))) 
        else:
            text.insert(INSERT, '\nAll subjects have the correct files!')
            text.see(END)
            text.update()

    # Handles Photos3D Contents Check  both R: and P: drives 
    elif phenotype == 'Photos3D':
        if studyID == '':
            for root, dirs, files in os.walk(path):
                for file in files:
                    for pattern in contents_dic[drive][phenotype]:
                        match = re.findall(pattern, file)
                        if match:
                            study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                            if 'tom' in file.lower():
                                file = study_ID_in_file[0] + '.tom'
                            elif 'clean_standard.tsb' in file.lower():
                                file = study_ID_in_file[0] + '_Clean_Standard.tsb'
                            elif 'clean_standard.pdf' in file.lower():
                                file = study_ID_in_file[0] + '_Clean_Standard.pdf'
                            elif 'clean_standard.txt' in file.lower():
                                file = study_ID_in_file[0] + '_Clean_Standard.txt'
                            elif 'clean.tsb' in file.lower():
                                file = study_ID_in_file[0] + '_Clean.tsb'
                            elif 'clean.obj' in file.lower():
                                file = study_ID_in_file[0] + '_Clean.obj'
                            elif 'clean.gif' in file.lower():
                                file = study_ID_in_file[0] + '_Clean.gif'
                            elif 'clean.mtl' in file.lower():
                                file = study_ID_in_file[0] + '_Clean.mtl'
                            elif 'clean.bmp' in file.lower():
                                file = study_ID_in_file[0] + '_Clean.bmp'
                            elif 'clean' in file.lower() and 'belgium.obj' in file.lower():
                                file = study_ID_in_file[0] + '_Clean_Belgium.obj'
                            elif 'tsb' in file.lower():
                                file = study_ID_in_file[0] + '.tsb'
                            elif 'obj' in file.lower():
                                file = study_ID_in_file[0] + '.obj'
                            elif 'mtl' in file.lower():
                                file = study_ID_in_file[0] + '.mtl'
                            elif '1.bmp' in file.lower():
                                file = study_ID_in_file[0] + '1.bmp'
                            elif '2.bmp' in file.lower():
                                file = study_ID_in_file[0] + '2.bmp'
                            elif '3.bmp' in file.lower():
                                file = study_ID_in_file[0] + '3.bmp'
                            #print('Appending', file)                        
                            text.insert(INSERT, '\nFile: {0}\n'.format(file))
                            text.see(END)
                            text.update()
                            text.delete('5.0','end')
                            on_fileserver.append(file)
        else:
            for root, dirs, files in os.walk(path):
                if studyID in root:
                    for file in files:
                        for pattern in contents_dic[drive][phenotype]:
                            match = re.findall(pattern, file)
                            if match:
                                study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                                if 'tom' in file.lower():
                                    file = study_ID_in_file[0] + '.tom'
                                elif 'clean_standard.tsb' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean_Standard.tsb'
                                elif 'clean_standard.pdf' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean_Standard.pdf'
                                elif 'clean_standard.txt' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean_Standard.txt'
                                elif 'clean.tsb' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean.tsb'
                                elif 'clean.obj' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean.obj'
                                elif 'clean.gif' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean.gif'
                                elif 'clean.mtl' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean.mtl'
                                elif 'clean.bmp' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean.bmp'
                                elif 'clean' in file.lower() and 'belgium.obj' in file.lower():
                                    file = study_ID_in_file[0] + '_Clean_Belgium.obj'
                                elif 'tsb' in file.lower():
                                    file = study_ID_in_file[0] + '.tsb'
                                elif 'obj' in file.lower():
                                    file = study_ID_in_file[0] + '.obj'
                                elif 'mtl' in file.lower():
                                    file = study_ID_in_file[0] + '.mtl'
                                elif '1.bmp' in file.lower():
                                    file = study_ID_in_file[0] + '1.bmp'
                                elif '2.bmp' in file.lower():
                                    file = study_ID_in_file[0] + '2.bmp'
                                elif '3.bmp' in file.lower():
                                    file = study_ID_in_file[0] + '3.bmp'
                                #print('Appending', file)                        
                                text.insert(INSERT, '\nFile: {0}\n'.format(file))
                                text.see(END)
                                text.update()
                                text.delete('5.0','end')
                                on_fileserver.append(file)

        for studyID in studyIDs_in_SQL:
            #print(studyID)
            if studyID[0] in exclude_list:
                continue
            else:
                should_have_STANDARD_TSB = '{}_Clean_Standard.tsb'.format(studyID[0])
                should_have.append(should_have_STANDARD_TSB)
                should_have_STANDARD_PDF = '{}_Clean_Standard.pdf'.format(studyID[0])
                should_have.append(should_have_STANDARD_PDF)
                should_have_STANDARD_TXT = '{}_Clean_Standard.txt'.format(studyID[0])
                should_have.append(should_have_STANDARD_TXT)

                if studyID[13] == '3dMD' and drive == 'P:':
                    should_have_TSB = '{}.tsb'.format(studyID[0])
                    should_have.append(should_have_TSB)

                elif studyID[13] == '3dMD' and drive == 'R:':
                    should_have_TSB = '{}.tsb'.format(studyID[0])
                    should_have.append(should_have_TSB)
                    should_have_Clean_TSB = '{}_Clean.tsb'.format(studyID[0])
                    should_have.append(should_have_Clean_TSB)
                    should_have_Clean_OBJ = '{}_Clean.obj'.format(studyID[0])
                    should_have.append(should_have_Clean_OBJ)
                    should_have_Clean_GIF = '{}_Clean.gif'.format(studyID[0])
                    should_have.append(should_have_Clean_GIF)
                    should_have_Clean_MTL = '{}_Clean.mtl'.format(studyID[0])
                    should_have.append(should_have_Clean_MTL)
                    should_have_Clean_BMP = '{}_Clean.bmp'.format(studyID[0])
                    should_have.append(should_have_Clean_BMP)
                    should_have_Clean_Belgium = '{}_Clean_Belgium.obj'.format(studyID[0])
                    should_have.append(should_have_Clean_Belgium)

                elif studyID[13] == 'Vectra' and drive == 'P:':
                    should_have_TOM = '{}.tom'.format(studyID[0])
                    should_have.append(should_have_TOM)

                elif studyID[13] == 'Vectra' and drive == 'R:':
                    should_have_OBJ = '{}.obj'.format(studyID[0])
                    should_have.append(should_have_OBJ)
                    should_have_MTL = '{}.mtl'.format(studyID[0])
                    should_have.append(should_have_MTL)
                    for num in range(1,4):
                        should_have_BMP = '{0}{1}.bmp'.format(studyID[0], str(num))
                        should_have.append(should_have_BMP)
                    should_have_Clean_OBJ = '{}_Clean.obj'.format(studyID[0])
                    should_have.append(should_have_Clean_OBJ)
                    should_have_Clean_MTL = '{}_Clean.mtl'.format(studyID[0])
                    should_have.append(should_have_Clean_MTL)
 
        missing = sorted(list(set(should_have).difference(set(on_fileserver))))

        text.delete('5.0','end')  
        text.insert(INSERT, '\nCheck the Individual Checklist and phenotype folder for the following:\n'.format(phenotype))
        if len(missing) >0:
            for studyID in missing:
                text.insert(INSERT,'{0} is missing\n'.format(studyID))
                text.see(END)
                text.update()
                #print(studyID, 'is missing')
            text.insert(INSERT,'Total number of files missing: {}'.format(len(missing)))
            #print('Total number of files missing: {}'.format(len(missing))) 
        else:
            text.insert(INSERT, '\nAll subjects have the correct files!')
            text.see(END)
            text.update()

    # Handles LipPhotos Contents Check  both R: and P: drives 
    elif phenotype == 'LipPhotos':
        if studyID =='':
            for root, dirs, files in os.walk(path):
                for file in files:
                    for pattern in contents_dic[drive][phenotype]:
                        match = re.findall(pattern, file)
                        if match:
                            study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                            if 'lil' in file.lower():
                                file = study_ID_in_file[0] + 'LIL.jpg'
                            elif 'LL' in file and 'inv' in file.lower():
                                file = 'LL_' + study_ID_in_file[0] + '_inv.jpg'
                            elif 'LL' in file and 'nor' in file.lower():
                                file = 'LL_' + study_ID_in_file[0] + '_nor.jpg'
                            elif 'LL' in file and 'pco' in file.lower():
                                file = 'LL_' + study_ID_in_file[0] + '_pco.jpg'
                            elif 'UL' in file and 'inv' in file.lower():
                                file = 'UL_' + study_ID_in_file[0] + '_inv.jpg'
                            elif 'UL' in file and 'nor' in file.lower():
                                file = 'UL_' + study_ID_in_file[0] + '_nor.jpg'
                            elif 'UL' in file and 'pco' in file.lower():
                                file = 'UL_' + study_ID_in_file[0] + '_pco.jpg'
                            elif 'p1.jpg' in file.lower():
                                file = study_ID_in_file[0] + 'p1.jpg'
                            elif 'p2.jpg' in file.lower():
                                file = study_ID_in_file[0] + 'p2.jpg'
                            elif 'p3.jpg' in file.lower():
                                file = study_ID_in_file[0] + 'p3.jpg'
                            elif 'p4.jpg' in file.lower():
                                file = study_ID_in_file[0] + 'p4.jpg'
                            elif 'p5.jpg' in file.lower():
                                file = study_ID_in_file[0] + 'p5.jpg'
                            elif 'p6.jpg' in file.lower():
                                file = study_ID_in_file[0] + 'p6.jpg'
                            elif 'p7.jpg' in file.lower():
                                file = study_ID_in_file[0] + 'p7.jpg'
                            #print('Appending', file)                        
                            text.insert(INSERT, '\nFile: {0}\n'.format(file))
                            text.see(END)
                            text.update()
                            text.delete('5.0','end')
                            on_fileserver.append(file)
        else:
            for root, dirs, files in os.walk(path):
                    for file in files:
                        if studyID in file:
                            #print(studyID, root, file)
                            for pattern in contents_dic[drive][phenotype]:
                                match = re.findall(pattern, file)
                                if match:
                                    study_ID_in_file = re.findall('[A-Za-z]{2}[0-9]{5}', file)
                                    #print('LIL test:', file.lower())
                                    if 'lil' in file.lower():
                                        file = study_ID_in_file[0] + 'LIL.jpg'
                                        #print('New LIL: ', file)
                                    elif 'LL' in file and 'inv' in file.lower():
                                        file = 'LL_' + study_ID_in_file[0] + '_inv.jpg'
                                    elif 'LL' in file and 'nor' in file.lower():
                                        file = 'LL_' + study_ID_in_file[0] + '_nor.jpg'
                                    elif 'LL' in file and 'pco' in file.lower():
                                        file = 'LL_' + study_ID_in_file[0] + '_pco.jpg'
                                    elif 'UL' in file and 'inv' in file.lower():
                                        file = 'UL_' + study_ID_in_file[0] + '_inv.jpg'
                                    elif 'UL' in file and 'nor' in file.lower():
                                        file = 'UL_' + study_ID_in_file[0] + '_nor.jpg'
                                    elif 'UL' in file and 'pco' in file.lower():
                                        file = 'UL_' + study_ID_in_file[0] + '_pco.jpg'
                                    elif 'p1.jpg' in file.lower():
                                        file = study_ID_in_file[0] + 'p1.jpg'
                                    elif 'p2.jpg' in file.lower():
                                        file = study_ID_in_file[0] + 'p2.jpg'
                                    elif 'p3.jpg' in file.lower():
                                        file = study_ID_in_file[0] + 'p3.jpg'
                                    elif 'p4.jpg' in file.lower():
                                        file = study_ID_in_file[0] + 'p4.jpg'
                                    elif 'p5.jpg' in file.lower():
                                        file = study_ID_in_file[0] + 'p5.jpg'
                                    elif 'p6.jpg' in file.lower():
                                        file = study_ID_in_file[0] + 'p6.jpg'
                                    elif 'p7.jpg' in file.lower():
                                        file = study_ID_in_file[0] + 'p7.jpg'
                                    #print('Appending', file)                        
                                    text.insert(INSERT, '\nFile: {0}\n'.format(file))
                                    text.see(END)
                                    text.update()
                                    text.delete('5.0','end')
                                    on_fileserver.append(file)

        # R: drive files
        if drive == 'R:':
            # To Process StudyIDs
            try:
                #print(studyID)
                toProcess_studyID_list = get_lip_to_process_studyIDs_SQL(phenotype, studyID) # get the ToProcess StudyIDs
            except:
                toProcess_studyID_list = []
                #print('get_lipToProcess_studyIDs_SQL function did not work as excepted')

            if toProcess_studyID_list != []:
                for studyID_toProcess in toProcess_studyID_list:
                    should_have_toProcess_LIL = studyID_toProcess[0] + 'LIL.jpg'
                    should_have.append(should_have_toProcess_LIL)
                    for num in range(1, 8):
                        #print(studyID_toProcess[0] + 'p{0}.jpg'.format(num))
                        should_have_toProcess_p = studyID_toProcess[0] + 'p{0}.jpg'.format(num)
                        should_have.append(should_have_toProcess_p)
            
            
            for studyID in studyIDs_in_SQL:
                #print(studyID)
                should_have_LL_INV = 'LL_{}_inv.jpg'.format(studyID)
                should_have.append(should_have_LL_INV)
                should_have_LL_NOR = 'LL_{}_nor.jpg'.format(studyID)
                should_have.append(should_have_LL_NOR)
                should_have_LL_PCO = 'LL_{}_pco.jpg'.format(studyID)
                should_have.append(should_have_LL_PCO)
                should_have_UL_INV = 'UL_{}_inv.jpg'.format(studyID)
                should_have.append(should_have_UL_INV)
                should_have_UL_NOR = 'UL_{}_nor.jpg'.format(studyID)
                should_have.append(should_have_UL_NOR)
                should_have_UL_PCO = 'UL_{}_pco.jpg'.format(studyID)
                should_have.append(should_have_UL_PCO)
        #print(should_have)
        # P: drive files
        if drive == 'P:':
            for studyID in studyIDs_in_SQL:
                for num in range(1, 8):
                    should_have_toProcess_p = studyID + 'p{0}.jpg'.format(num)
                    should_have.append(should_have_toProcess_p)
                should_have_LIL = '{}LIL.jpg'.format(studyID)
                should_have.append(should_have_LIL)
                should_have_LL_PSD = 'LL_{}.psd'.format(studyID)
                should_have.append(should_have_LL_PSD)
                should_have_LL_PSD = 'UL_{}.psd'.format(studyID)
                should_have.append(should_have_LL_PSD)
        #print(set(should_have))
        #print()
        #print(set(on_fileserver))
        missing = sorted(list(set(should_have).difference(set(on_fileserver))))
        #print(missing)
        text.delete('5.0','end')  
        text.insert(INSERT, '\nCheck the Individual Checklist and phenotype folder for the following:\n'.format(phenotype))
        if len(missing) >0:
            for studyID in missing:
                text.insert(INSERT,'{0} is missing\n'.format(studyID))
                text.see(END)
                text.update()
                #print(studyID, 'is missing')
            text.insert(INSERT,'Total number of files missing: {}'.format(len(missing)))
            #print('Total number of files missing: {}'.format(len(missing))) 
        else:
            text.insert(INSERT, '\nAll subjects have the correct files!')
            text.see(END)
            text.update()

    text.configure(state='disabled')


def get_submit():
    if phenotype_combo.get() == '':
        messagebox.showwarning('Phenotype', 'Must choose a "Phenotype" to run')

    if check_combo.get() == 'Folders Check':
        check_folder(drive_combo.get(), phenotype_combo.get(), studyID_entry.get())
    elif check_combo.get() == 'Spelling Check':
        check_spelling(drive_combo.get(), phenotype_combo.get(), studyID_entry.get())    
    elif check_combo.get()  == 'Contents Check':
        check_contents(drive_combo.get(), phenotype_combo.get(), studyID_entry.get())
    else:
        messagebox.showwarning('Check', 'Must choose a "Check" to run')


def get_savelog():
    log_contents = text.get(1.0, 'end')
    #print(log_contents)
    with asksaveasfile(title='Save Output', mode='a+', defaultextension='.csv', filetypes =(('csv', '.csv'),('txt', '.txt'))) as create_log:
        for line in log_contents:
            create_log.writelines(line)


def get_about():
    messagebox.showinfo('About', '''
    Created by: Joel Anderton
    Created date: 7/22/2019

    OFC2 Check files on file server
    Version 1.1
    
    Only works for the OFC2 Study
    Checks the following:
       1. Folders Check - File in correct folder.
       2. Spelling Check - Folder has an acceptable StudyID.
       3. Contents Check - Subject contains all necessary files.
    
    Updates:
    9/9/2019 - Excluded subjects because unusable, not received, or lip pits. 

    ''')


root = Tk()
root.geometry('1480x700+150+80')
root.state('zoom')
root.update_idletasks()

studyID = StringVar()
drive = StringVar()
phenotype = StringVar()
check = StringVar()

root.title('Phenotype File and Folder Checking v. 1.1')

frame = Frame(root, width=200, height=310, highlightbackground="black", highlightcolor="black", highlightthickness=1, bd=0)
frame.place(x=30, y=160)

#Drive Combobox
drive_label = ttk.Label(root, text='Drive:')
drive_label.place(x=40, y=180)
drive_combo = ttk.Combobox(root, textvariable=drive, values=('R:', 'P:'), width=5)
drive_combo.place(x=110, y=180)
drive_combo.set('R:')

# Phenotype Combobox
phenotype_label = ttk.Label(root, text='Phenotype:')
phenotype_label.place(x=40, y=220)
phenotype_combo = ttk.Combobox(root, textvariable=phenotype, values=('LipUltrasound', 'LipPhotos', 'LHFPhoto', 'IntraoralPhotos', 
                                                                     'PalateVideo', 'Photos3D', 'DentalImpression', 'HandScan', 'SpeechVideos' ), width=15)
phenotype_combo.place(x=110, y=220)

# Check Combobox
check_label = ttk.Label(root, text='Check:')
check_label.place(x=40, y=260)
check_combo = ttk.Combobox(root, textvariable=check, values=('Folders Check', 'Spelling Check', 'Contents Check',), width=15)
check_combo.place(x=110, y=260)

#StudyID Entry
studyID_label = ttk.Label(root, text='StudyID:')
studyID_label.place(x=40, y=300)
studyID_entry = ttk.Entry(root, textvariable=studyID, width=15)
studyID_entry.place(x=110, y=300)

#Submit Button
submit_button = ttk.Button(root, text='Submit', width=10, command=get_submit)
submit_button.place(x=90, y=340)

#Save Log Button
savelog_button = ttk.Button(root, text='Save Log', width=10, command=get_savelog)
savelog_button.place(x=90, y=370)

# Close button
closeButton = ttk.Button(root, text='Close', width=10, command=root.destroy)
closeButton.place(x=90, y=400)

# About button
aboutButton = ttk.Button(root, text='About', width=10, command=get_about)
aboutButton.place(x=90, y=430)

# Scroll bar
scroll = Scrollbar(root)
scroll.pack(side=RIGHT, fill=Y)

#Output window
text_label = Label(root, text='Results')
text_label.place(x=250, y=20)
text = Text(root, width=140, height=40, borderwidth=3, font=('calibri',11), wrap='word', relief='groove', yscrollcommand=scroll.set)
text.place(x=250, rely=0.06)
scroll.config(command=text.yview)

root.mainloop()

