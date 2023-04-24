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
from backupscfg import jobs, smtp, backupDir, logFile # configuration file
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

## functions
def writeLog(success, message, dateTimeStamp):
    """
    Write a message to log file.
    
    Parameters:
        success (boolean): True -> write success message
                           False -> write failure message. 
        
        message (string): message to display.
        
        dateTimeStamp (string): Date and time when program was run.
    """
    
    try:
        file = open(logFile, "a")
        logMessage = ("SUCCESS " if success else "FAILURE ") + dateTimeStamp + " " + message + "\n"
        file.write(logMessage)
        file.close()
    
    except FileNotFoundError:
        print("ERROR: Log file " + logFile + " does not exist", file=sys.stderr)
   
    except IOError:
        print("ERROR: Log file " + logFile + " is not accessible", file=sys.stderr)
   
def sendEmail(message, dateTimeStamp):
    """
    Send an email message to the specified recipient.
    
    Parameters:
        message (string): message to send.
        
        dateTimeStamp (string): Date and time when program was run.
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
        
    except Exception as e:
        print("ERROR: Send email failed: " + str(e), file=sys.stderr)

def errorProcessing(errorMessage, dateTimeStamp):
    """ 
    Display error message to the screem, email it to the administrator and
    write it to the log file backup.log.
        
    Parameters:
        errorMessage (string): message to display.
        
        dateTimeStamp (string): Date and time when program was run.
    """

    # write error message to standard error
    print("ERROR: " + errorMessage, file=sys.stderr)
    
    # write error message to log file
    writeLog(False, errorMessage, dateTimeStamp)
    
    # email error message to administrator
    #sendEmail(errorMessage, dateTimeStamp)

YELLOWBLACK = 1
BLUEBLACK = 2

def getDims(win):
    rows = curses.LINES
    cols = curses.COLS
    win.addstr(f"Lines: {rows}, Rows: {cols}\n")
    win.refresh()
    win.addstr("Press any key to continue.")
    win.getch()
    return rows, cols

def showPage(win, title, rows, cols):
    win.clear()
    win.addstr(0, int((cols - len(title)) / 2), title, curses.color_pair(YELLOWBLACK) | curses.A_BOLD)
    win.addstr(1, 0, "   Job    Source                        Destination", curses.color_pair(YELLOWBLACK))
    win.addstr(rows - 2, 0, "[ ]un [ ]iew [ ]dd [ ]hange [ ]elete [ ]Scroll E[ ]it", curses.color_pair(BLUEBLACK))
    win.addstr(rows - 2, 1, "R", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 7, "V", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 14, "A", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 20, "C", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 29, "D", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 38, chr(8597), curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 49, "X", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    curses.setsyx(rows - 1, 0)
    win.refresh()

def listBackups(jobsList, rows, cols, firstRow):
    jobsList.addstr(0, 0, "1  Job1   /src/file.txt                 /backups")
    jobsList.addstr(1, 0, "2  Job2   /src/file.txt                 /backups")
    jobsList.addstr(2, 0, "3  Job3   /src/file.txt                 /backups")
    jobsList.addstr(3, 0, "4  Job4   /src/file.txt                 /backups")
    jobsList.addstr(4, 0, "5  Job5   /src/file.txt                 /backups")
    jobsList.addstr(5, 0, "6  Job6   /src/file.txt                 /backups")
    
    jobsList.refresh(firstRow, 0, 2, 0, rows - 3, cols - 1)
    curses.setsyx(rows - 1, 0)

def maintainBackups(stdScr):
    curses.init_pair(YELLOWBLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(BLUEBLACK, curses.COLOR_BLUE, curses.COLOR_BLACK)
    stdScr = curses.initscr()
    stdScr.leaveok(True)
    rows, cols = getDims(stdScr)
    showPage(stdScr, "SuniTAFE Backups", rows, cols)
  
    jobsList = curses.newpad(100, 100)
    firstRow = 0
    lastRow = 5
    listBackups(jobsList, rows, cols, firstRow)
   
    while True: 
        key = stdScr.getch()
        
        if (key == curses.KEY_DOWN) and (firstRow < lastRow):
            firstRow += 1
            listBackups(jobsList, rows, cols, firstRow)
        elif (key == curses.KEY_UP) and (firstRow > 0):
            firstRow -= 1
            listBackups(jobsList, rows, cols, firstRow)
        elif key == ord('x'):
            break
             
    curses.endwin()

## main function
def main():
    """
    Main function.  Backup a series of files or directories referred to by
    command line argument and specified in jobs in the backupscfg.py file.
    Successful backups are written to the log file, backup.log.
    Errors are displayed on the screen, emailed to the adminstrator and 
    written to the log file, backup.log.
    Details of files and directories to be backed-up and other
    configuration details are specified in the configuration file,
    backupscfg.py.
    """

    try:
        
        # get current date time stamp
        dateTimeStamp = datetime.now().strftime("%Y%m%d-%H%M%S")  
        
        # check for job name as command line argument
        # error condition
        if len(sys.argv) > 2:
            errorProcessing("Usage: backups.py job1 # immediate mode, run job1 | backups.py # maintenance mode", dateTimeStamp)
            
        # enter backups maintenance mode
        elif len(sys.argv) == 1:
            wrapper(maintainBackups)
        
        # process job from command line    
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
        print("ERROR: backups.py program failed: " + str(e))
  
## call main function  
if __name__ == "__main__":
    main()