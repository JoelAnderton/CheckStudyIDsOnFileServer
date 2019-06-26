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


def get_studyIDs_SQL(phenotype, studyID=''):
    """Finds completed StudyIDs in SQL"""
    text.config(state='normal')
    text.delete('1.0', 'end')
    text.insert('1.0', '\nSearching SQL for StudyIDs\n')
    text.see(END)
    text.update()
    print('Searching SQL for StudyIDs')
    studyID_list = []
    studyID_list.append(studyID)
    connection = sql_connection()
    cur = connection.cursor()

    if studyID == None: # if not given an individual StudyID
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
       
        FROM IndividualChecklistExported
        WHERE {0} = 1 AND [StudyID] = ?
        '''.format(phenotype))
        cur.execute(sqlcode, studyID_list)

    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        #print(row)
        text.insert('1.0 + 3 lines', 'StudyID: {0}'.format(row[0:][0]))
        text.see(END)
        text.update()
        text.delete('1.0 + 3 lines','end')
        print('StudyID: {0}'.format(row[0:][0]), end='\r')
        studyIDs_in_SQl_list.append(row)
    print('StudyID: Done!     ')
    print()
    return studyIDs_in_SQl_list


def get_studyIDs_Server(drive, phenotype, studyID = ''):
    """Finds StudyIDs used on file server"""
    text.config(state='normal')
    text.delete('1.0', 'end')
    text.insert('1.0', 'Searching file server in the {0} phenotype folder for StudyIDs\n'.format(phenotype))
    text.see(END)
    text.update()
    print('\nSearching file server in the {0} phenotype folder for StudyIDs'.format(phenotype))
 
    path = get_file_paths(drive, phenotype)

    studyID_list = []
    if studyID == None:
        for root, dirs, files in os.walk(path):
            for dir in dirs:
                match = re.search("[A-Za-z]{2}[0-9]{5}", dir)    
                if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                    text.insert('1.0', 'StudyID: {0}'.format(dir[match.start():match.end()]))
                    text.see(END)
                    text.update()
                    text.delete('1.0','end')
                    print('StudyID:', dir[match.start():match.end()], end='\r')
                    studyID_list.append({dir[match.start():match.end()]:os.path.join(root, dir[match.start():match.end()])}) 
    else:
        for root, dirs, files in os.walk(path):
            if studyID in dirs:
                for dir in dirs:
                    match = re.search("[A-Za-z]{2}[0-9]{5}", dir)    
                    if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                        text.insert('1.0', 'StudyID: {0}'.format(dir[match.start():match.end()]))
                        text.see(END)
                        text.update()
                        text.delete('1.0','end')
                        print('StudyID:', dir[match.start():match.end()], end='\r')
                        studyID_list.append({dir[match.start():match.end()]:os.path.join(root, dir[match.start():match.end()])})
    text.insert('1.0', 'StudyID: Done!            ')
    print('StudyID: Done!     ')
    print()
    return studyID_list



def check_folder(drive, phenotype, studyID = ''):
    """Check if file is in the correct folder"""
    text.config(state='normal')
    text.delete('1.0', 'end')
    text.insert('1.0', '************************************\nFolder Check for {0}\n************************************'.format(phenotype))
    text.see(END)
    text.update()
    print('************************************\nFolder Check for {0}\n************************************'.format(phenotype))
    path = get_file_paths(drive, phenotype)
        
    wrong_folder = []

    if studyID == '':
        for root, dirs, files in os.walk(path):
            for file in files:
                
                match = re.search("[A-Za-z]{2}[0-9]{5}", file) 
                if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):                
                    text.insert('1.0', 'Folder check for: {0}'.format(file[match.start():match.end()]))
                    text.see(END)
                    text.update()
                    text.delete('1.0','end')
                    print('Checking files for:', file[match.start():match.end()], end='\r')
                    if file[match.start():match.end()] not in root:
                       wrong_folder.append(os.path.join(root, file))
    else:
        for root, dirs, files in os.walk(path):
            if studyID in root:
                for file in files:
                    match = re.search("[A-Za-z]{2}[0-9]{5}", file) 
                    if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                        text.insert('1.0', 'Folder check for: {0}'.format(file[match.start():match.end()]))
                        text.see(END)
                        text.update()
                        text.delete('1.0','end')
                        print('Checking files for:', file[match.start():match.end()], end='\r')
                        if file[match.start():match.end()] not in root:
                           wrong_folder.append(os.path.join(root, file))

 

    if len(wrong_folder) >0:
        text.insert('1.0', 'Check that the file is in the correct folder for the following:\n')
        text.see(END)
        text.update()
        print('Check that the file is in the correct folder for the following:')
        for file in wrong_folder:
            text.insert('1.0 + 2 lines','{0}\n'.format(file))            
    else:
        text.insert('1.0', 'All files are in their correct folders!')
        text.see(END)
        text.update()
        print('All files are in their correct folders!')
    text.config(state='disabled')

def check_spelling(drive, phenotype, studyID = ''):
    """Check if file has the correct spelling for a StudyID"""
    text.config(state='normal')
    text.delete('1.0', 'end')
    text.insert('1.0', '************************************\nFolder Check for {0}\n************************************'.format(phenotype))
    text.see(END)
    text.update()
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

    # Gets StudyIDs from SQL
    studyIDs_in_SQL = get_studyIDs_SQL(phenotype=phenotype, studyID=studyID)
    only_StudyIDs = []
    for row in studyIDs_in_SQL:   # get only the StudyIDs and add them to the only_StudyIDs list
        only_StudyIDs.append(row[0:][0])
    
    #print(only_StudyIDs)

    if studyID == '':
        diff = set(studyIDs_on_Server).difference(set(only_StudyIDs))
        if len(diff) > 0:
            text.insert('1.0', 'List of StudyIDs that should not have completed {0}.\nCheck the Individual Checklist and that the StudyID is spelled correctly:\n'.format(phenotype))
            text.see(END)
            text.update()
            text.delete('1.0','end')
            print('List of StudyIDs that should not have completed {0}.\nCheck the Individual Checklist and that the StudyID is spelled correctly:\n'.format(phenotype))
            for file in diff:
               print(file, folder_paths[file] )
        else:
            print('All files are spelled correct!')
    else:
        
        if studyID not in studyIDs_on_Server and studyID in only_StudyIDs:
            text.insert('1.0', 'StudyID: {0} is a valid StudyID, but DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
            text.see(END)
            text.update()
            text.delete('1.0','end')
            print('StudyID: {0} is a valid StudyID, but DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
        elif studyID in studyIDs_on_Server and studyID not in only_StudyIDs:
            text.insert('1.0', 'StudyID: {0} is a valid StudyID, but DOES exist in the {1} phenotype folder'.format(studyID, phenotype))
            text.see(END)
            text.update()
            text.delete('1.0','end')
            print('StudyID: {0} is NOT a valid StudyID, but DOES exist in the {1} phenotype folder'.format(studyID, phenotype))
            print(studyID, folder_paths[studyID])
        elif studyID not in studyIDs_on_Server and studyID not in only_StudyIDs:
            text.insert('1.0', 'StudyID: {0} is NOT a valid StudyID and DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
            text.see(END)
            text.update()
            text.delete('1.0','end')
            print('StudyID: {0} is NOT a valid StudyID and DOES NOT exist in the {1} phenotype folder'.format(studyID, phenotype))
        else:
            text.insert('1.0', 'StudyID: {0} is spelled correctly on server!'.format(studyID))
            text.see(END)
            text.update()
            text.delete('1.0','end')
            print('StudyID: {0} is spelled correctly on server!'.format(studyID))
            print(studyID, folder_paths[studyID])
    print()

def check_contents(drive, phenotype, studyID=''):
    contents_dic = {'R:':{'HandScan':{'.tif':1, 
                                '.tps':2},
                    'PalateVideo':{'.mov':1},
                    'Photos3D':{'.tsb':3, 
                                '.bmp':1, 
                                '.gif':1, 
                                '.mtl':1, 
                                '.obj':2, 
                                '.pdf':1, 
                                '.txt':1 }

                        }
                    }

    #studyIDs_and_paths = get_studyIDs_Server(drive=drive, phenotype=phenotype, studyID=studyID)
    #studyIDs_in_SQL = get_studyIDs_SQL(phenotype=phenotype, studyID=studyID)
    
    path = get_file_paths(drive, phenotype)

    # Get all Files and put them in a list
    all_files = []
    if studyID == None:
        for root, dirs, files in os.walk(path):
            for file in files:
                match = re.search("[A-Za-z]{2}[0-9]{5}", file)
                if match and ('Library' in root or '1ToProcess' in root or '1New_Data_Drop' in root or 'Colombia' in root or 'Lancaster' in root or 'Philippines' in root or 'Pittsburgh' in root or 'Puerto Rico' in root):
                    print('Checking files for:', file[match.start():match.end()], end='\r')
                    extension = os.path.splitext(file)[1]
                    all_files.append('{0}, {1}'.format(file[match.start():match.end()], extension))

    # Count the number of files in the list 
    count_all_files_list = []
    for file in all_files:
        count_all_files_list.append('{0}, {1}'.format(file, all_files.count(file)))

    count_all_files_set = set(count_all_files_list) # make the list unique for each file type 
    count_all_files_list_sorted = sorted(list(count_all_files_set))
    for file in count_all_files_list_sorted:
        print(file)





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


def get_about():
    pass

#drive = 'R:' 
#phenotype = 'Photos3D'
#get_submit(drive, phenotype)


root = Tk()
root.geometry('1480x700+150+80')
root.state('zoom')
root.update_idletasks()

studyID = StringVar()
drive = StringVar()
phenotype = StringVar()
check = StringVar()

root.title('Phenotype File and Folder Checking v. 1.0')

frame = Frame(root, width=200, height=290, highlightbackground="black", highlightcolor="black", highlightthickness=1, bd=0)
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

# Close button
closeButton = ttk.Button(root, text='Close', width=10, command=root.destroy)
closeButton.place(x=90, y=370)

# About button
aboutButton = ttk.Button(root, text='About', width=10, command=get_about)
aboutButton.place(x=90, y=400)

# Scroll bar
scroll = Scrollbar(root)
scroll.pack(side=RIGHT, fill=Y)

#Output window
text_label = Label(root, text='Results')
text_label.place(x=250, y=20)
text = Text(root, width=140, height=40, borderwidth=3, wrap='word', relief='groove', yscrollcommand=scroll.set)
text.place(x=250, rely=0.06)
scroll.config(command=text.yview)

root.mainloop()