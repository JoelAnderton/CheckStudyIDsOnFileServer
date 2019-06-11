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


def studyIDs_in_SQL():
    """Finds StudyIDs already imported in SQL"""
    connection = sql_connection()
    cur = connection.cursor()

    sqlcode = ('''  
    SELECT StudyID
    FROM IndividualChecklistExported

    ''')
    cur.execute(sqlcode)
    studyIDs_in_SQl_list = []
    for row in cur.fetchall():
        studyIDs_in_SQl_list.append(row[0])
    return studyIDs_in_SQl_list

def studyIDs_on_Server():
    """Finds StudyIDs used on file server"""
    pass

def main():
    studyID_list = studyIDs_in_SQL()
    for studyID in studyID_list:
        print(studyID)

if __name__ == '__main__': 
    main()
