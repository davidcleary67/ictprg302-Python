#!/usr/bin/python3

"""
Program:   backups.py
Version:   1.0
Date:      11 Apr 2023
Author:    David Cleary
Licencing: Copyright 2023 SuniTAFE. All rights reserved.
"""

## imports

import sys
import os
import pathlib
import shutil
import smtplib
from datetime import datetime
from backupscfg import jobs, smtp, backupDir, logFile

## functions
def writeLog(success, message, dateTimeStamp):
    """ Write message to log file.
    """
    
    try:
        file = open(logFile, "a")
        logMessage = ("SUCCESS " if success else "FAILURE ") + dateTimeStamp + " " + message + "\n"
        file.write(logMessage)
        file.close()
    
    except FileNotFoundError:
        print("ERROR: Log file " + logFile + " does not exist")
   
    except IOError:
        print("ERROR: Log file " + logFile + " is not accessible")
   
def sendEmail(message, dateTimeStamp):
    """ Send an email message to the specified recipient."
    """
    
    # create email message
    email = 'To: ' + smtp["recipient"] + '\n' + 'From: ' + smtp["sender"] + '\n' + 'Subject: Backup Error\n\n' + message + '\n'

    # connect to email server and send email
    try:
        smtp_server = smtplib.SMTP(smtp["server"], smtp["port"])
        smtp_server.ehlo()
        smtp_server.starttls()
        smtp_server.ehlo()
        smtp_server.login(smtp["user"], smtp["password"])
        smtp_server.sendmail(smtp["sender"], smtp["recipient"], email)
        smtp_server.close()
        
    except:
        print("ERROR: Unable to send email")

def errorProcessing(errorMessage, dateTimeStamp):
    """ Display error message to the screem, email it to the administrator and
        write it to the log file, backup.log.
    """
    
    # display error message on screen
    print("ERROR: " + errorMessage)
    
    # write error message to log
    writeLog(False, errorMessage, dateTimeStamp)
    
    # email error message to administrator
    #sendEmail(errorMessage, dateTimeStamp)

## main function
def main():
    """ Main function.  Backup a series of files or directories referred to by
        command line argument and specified in jobs in the backupscfg.py file.
        Successful backups are written to the log file, backup.log.
        Errors are displayed on the screen, emailed to the adminstrator and 
        written to the log file, backup.log.
    """

    try:
        
        # get current date time stamp
        dateTimeStamp = datetime.now().strftime("%Y%m%d-%H%M%S")  
        
        # check for job name as command line argument
        if len(sys.argv) != 2:
            errorProcessing("Job name missing from command line", dateTimeStamp)
        else:
            
            # get job name from command line and check it is included
            # in jobs dictionary
            jobName = sys.argv[1]
            
            if not jobName in jobs:
                errorProcessing("Job: " + jobName + " not found", dateTimeStamp)
            
            else:
                
                # loop through source files/directories to be backed-up
                for src in jobs[jobName]:
                
                    # check file/directory exists
                    if not os.path.exists(src):
                        errorProcessing("Source file/directory: " + src + " does not exist", dateTimeStamp)
                    
                    else:
                        
                        # get destination directory and check it exists
                        srcPath = pathlib.PurePath(src)
                        
                        if not os.path.exists(backupDir):
                            errorProcessing("Destination directory: " + backupDir + " does not exist", dateTimeStamp)
                            
                        else:
                            
                            # copy source directory/file to destination directory
                            dst = backupDir + "/" + srcPath.name + "-" + dateTimeStamp
                            
                            # copy source directory
                            if pathlib.Path(src).is_dir():
                                shutil.copytree(src, dst)
                                
                            # copy source file
                            else:
                                shutil.copy2(src, dst)
                            
                            # write success message to log
                            writeLog(True, "Backed-up " + src + " to " + dst, dateTimeStamp)
    
    except Exception as e:
        print("ERROR: backup.py program failed: " + str(e))
  
## call main function  
if __name__ == "__main__":
    main()