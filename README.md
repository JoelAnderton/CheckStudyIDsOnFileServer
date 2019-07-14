# CheckStudyIDsOnFileServer
Python app to check that StudyIDs on the file server are spelled correctly and contain the correct files.

* Check that the OFC2 StudyIDs that name the files on the file server match the IDs in SQL
* Check they did what they were suppose to do
* Check they are in the correct folder
* Check they contain all the right files

(customized to work for studies at the CCDG clinic at the University of Pittsburgh)

# What I learned
* Use string interpolation to manipulate SQL code so I only needed 1 function to get SQL data instead of seperate function for each phenotype
* Practice regex expressions
* Use itertools module
* Find and highlight differences in text and display those differences it on a tkinter textbox
