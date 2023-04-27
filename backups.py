#!/usr/bin/python3

"""
Program:   backups.py
Version:   2.0
Date:      27 Apr 2023
Author:    David Cleary
Licencing: Copyright 2023 SuniTAFE. All rights reserved.
"""

## imports

import sys
import os
import pathlib
import shutil
import smtplib
import time
from datetime import datetime
from backupscfg import jobs, smtp, backupDir, logFile # configuration file
import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

## global variables and constants

YELLOWBLACK = 1
BLUEBLACK = 2
GREENBLACK = 3

saved = True

backupsFile = "backups.dat"

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
        file.write(message + "\n")
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

def errorProcessing(success, errorMessage, dateTimeStamp, interactive = False, win = None):
    """ 
    Display error message to the screem, email it to the administrator and
    write it to the log file backup.log.
        
    Parameters:
        errorMessage (string): message to display.
        
        dateTimeStamp (string): Date and time when program was run.
        
        interactive (Boolean): True -> program is running in interactive mode
                               False -> program is running in immediate mode
                              
        win (curses pad): if interactive mode -> screen pad on which to display 
                          messsage
    """

    if interactive:
        win.addstr(errorMessage + "\n")
    elif not success:
        # write error message to standard error
        print("ERROR: " + errorMessage, file=sys.stderr)
    
        # email error message to administrator
        #sendEmail(errorMessage, dateTimeStamp)
        
    # write error message to log file
    writeLog(success, errorMessage, dateTimeStamp)


def getDims(win, pause):
    """ 
    Interactive mode function
    Get screen dimensions in rows and columns.
        
    Parameters:
        win (curses screen): return dimensions of this screen
        
        pause (Boolean): True -> display dimensions and pause
    
    Returns:
        rows (integer): screen rows
        
        cols (integer): screen columns
    """
    rows = curses.LINES
    cols = curses.COLS
    win.addstr(f"Lines: {rows}, Rows: {cols}\n")
    win.refresh()
    if pause:
        win.addstr("Press any key to continue.")
        win.getch()
    return rows, cols

def showBackupLabel(win):
    """ 
    Interactive mode function
    Display backup directory label
        
    Parameters:
        win (curses window): window in which to display label
    """
    
    win.addstr(1, 0, "[ ]ackup directory: ", curses.color_pair(BLUEBLACK))
    win.addstr(1, 1, "B", curses.color_pair(BLUEBLACK) | curses.A_BOLD)

def showPage(win, rows, cols):
    """ 
    Interactive mode function
    Display main screen labels and menu.
        
    Parameters:
        win (curses window): window in which to display labels and menu
        
        rows (integer): screen rows
        
        cols (integer): screen columns
    """

    win.clear()
    win.addstr(0, int((cols - 16) / 2), "SuniTAFE Backups", curses.color_pair(YELLOWBLACK) | curses.A_BOLD)
    showBackupLabel(win)
    win.addstr(2, 0, "   Jobname   Source files and directories", curses.color_pair(YELLOWBLACK))
    win.addstr(rows - 2, 0, "Job: [ ]un [ ]iew [ ]dd [ ]hange [ ]elete [ ]Scroll, [ ]ave E[ ]it", curses.color_pair(BLUEBLACK))
    win.addstr(rows - 2, 6, "R", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 12, "V", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 19, "A", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 25, "C", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 34, "D", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 43, chr(8597), curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 54, "S", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.addstr(rows - 2, 62, "X", curses.color_pair(BLUEBLACK) | curses.A_BOLD)
    win.refresh()

def listBackups(jobs, jobsList, rows, cols, firstRow):
    """ 
    Interactive mode function
    Add all backup jobs to a curses pad and display the pad taking into account
    current scroll settings.
        
    Parameters:
        jobs (list): all backup jobs with names and sources
        
        jobsList (curses pad): window in which to display backup jobs
        
        rows (integer): screen rows
        
        cols (integer): screen columns
        
        win (curses window): window in which to display labels and menu
        
        rows (integer): screen rows
        
        cols (integer): screen columns
        
        firstRow (integer): index of first backup row to display
    """

    row = 0 
    jobsList.clear()
    for job in jobs:
        jobStr = f"{row + 1:<3}{job['name']:<10}{job['source']:<}"
        jobsList.addstr(row, 0, jobStr)
        row += 1
    
    jobsList.refresh(firstRow, 0, 3, 0, rows - 3, cols - 1)


def loadBackups():
    """ 
    Interactive mode function
    Load all backup jobs from a file.
    
    Returns:
        backupDir (string): backup directory
        
        jobs (list): all backup jobs with names and sources
    """

    try:
        jobs = []
        file = open(backupsFile, "r")
        jobData = file.readlines()
        first = True
        for jobStr in jobData:
            if first:
                backupDir = jobStr.rstrip("\n")
                first = False
            else:
                jobList = jobStr.split(" ")
                jobs.append({"name": jobList[0].rstrip("\n"), "source": jobList[1].rstrip("\n")})
        file.close()
        return backupDir, jobs

    except FileNotFoundError:
        print("ERROR: Backups data file " + backupsFile + " does not exist", file=sys.stderr)
   
    except IOError:
        print("ERROR: Backups data file " + backupsFile + " is not accessible", file=sys.stderr)

def saveBackups(backupDir, jobs):
    """ 
    Interactive mode function
    Save all backup jobs to a file.
        
    Parameters:
        backupDir (string): backup directory
        
        jobs (list): all backup jobs with names and sources
    """

    try:
        file = open(backupsFile, "w")
        file.write(backupDir.rstrip(" \t\n") + "\n")
        for job in jobs:
            file.write(job["name"].rstrip(" \t\n") + " " + job["source"].rstrip(" \t\n") + "\n")
        file.close()

    except FileNotFoundError:
        print("ERROR: Backups data file " + backupsFile + " does not exist", file=sys.stderr)
   
    except IOError:
        print("ERROR: Backups data file " + backupsFile + " is not accessible", file=sys.stderr)
   
def showMessage(win, message, autoClear = True, delay=1):
    win.clear()
    win.addstr(0, 0, message, curses.color_pair(YELLOWBLACK) | curses.A_REVERSE)
    win.refresh()
    if autoClear:
        time.sleep(delay)
        win.clear()
        win.refresh()

def getInput(win, prompt, maxLen = 20):
    curses.echo()
    win.addstr(0, 0, prompt, curses.color_pair(GREENBLACK))
    win.refresh()
    inp = win.getstr(0, len(prompt), maxLen).decode(encoding="utf-8")
    curses.noecho()
    win.clear()
    win.refresh()
    return inp

def getIntInput(win, prompt, maxLen = 20):
    curses.echo()
    win.addstr(0, 0, prompt, curses.color_pair(GREENBLACK))
    win.refresh()
    inp = win.getstr(0, len(prompt), maxLen).decode(encoding="utf-8")
    curses.noecho()
    win.clear()
    win.refresh()
    try:
        intInp = int(inp)
    except:
        intInp = 0
    return intInp

def updateInput(win, prompt, maxLen = 20):
    #curses.echo() 
    box = Textbox(win, insert_mode = True)
    win.addstr(0, 0, prompt, curses.color_pair(GREENBLACK))
    win.refresh()
    inp = box.edit()
    data = box.gather()
    return inp

def keyList(inpList):
    outList = []
    for k in inpList:
        outList.append(ord(k.lower()))
        outList.append(ord(k.upper()))
    return outList
    
def showBackupDir(win, backupDir):
    win.addstr(0, 0, backupDir)
    win.refresh()

def hideCursor(win):
    win.addstr(0, 0, "")
    win.refresh()
    win.clear()
    win.refresh()
   
def showBackup(win, update = False):
    win.clear()
    win.addstr(0, 0, "Jobname: ", curses.color_pair(YELLOWBLACK))
    win.addstr(2, 0, "Source files and directories: ", curses.color_pair(YELLOWBLACK))
    win.addstr(2, 30, "(Ctrl-G to exit)" if update else "", curses.color_pair(YELLOWBLACK))
    win.refresh()

def showField(win, field):
    win.clear()
    win.addstr(0, 0, field)
    win.refresh()

def getField(win, text, dispWin, message, new = False):
    field = ""
    while field == "":
        if new:
            showField(win, "")
        field = text.edit()
        if field == "":
            showMessage(dispWin, message)
    return field
    
def showRun(win, jobName):
    win.clear()
    win.addstr(0, 0, "Jobname: ", curses.color_pair(YELLOWBLACK))
    win.addstr(0, 9, jobName)
    win.addstr(", Log entries", curses.color_pair(YELLOWBLACK))
    win.refresh()

def setBackupDir(win, text):
    win.refresh()
    backupDir = text.edit().rstrip(" \t\n")
    return backupDir

def addBackup(jobWin, dispWin, jobnameWin, jobnameText, sourceWin, sourceText, jobs):
    showBackup(jobWin, True)
    jobname = getField(jobnameWin, jobnameText, dispWin, "Invalid jobname.", True)
    source = getField(sourceWin, sourceText, dispWin, "Invalid source files and directories.", True)
    jobs.append({"name": jobname.replace(" ", "").replace("\t", "").replace("\n", ""), "source": source.replace(" ", "").replace("\t", "").replace("\n", "")})

def viewBackup(jobWin, dispWin, jobnameWin, sourceWin, job):
    showBackup(jobWin)
    showField(jobnameWin, job["name"])
    showField(sourceWin, job["source"])

def changeBackup(jobWin, dispWin, jobnameWin, jobnameText, sourceWin, sourceText, job):
    showBackup(jobWin, True)
    showField(jobnameWin, job["name"])
    showField(sourceWin, job["source"])
    jobnameWin.refresh()
    jobname = getField(jobnameWin, jobnameText, dispWin, "Invalid jobname.")
    job["name"] = jobname.replace(" ", "").replace("\t", "").replace("\n", "") if jobname != "" else job["name"]
    sourceWin.refresh()
    source = getField(sourceWin, sourceText, dispWin, "Invalid source files and directories.")
    job["source"] = source.replace(" ", "").replace("\t", "").replace("\n", "") if source != "" else job["source"]

def runBackup(runWin, runPad, job, backupDir):
    global dateTimeStamp
    
    showRun(runWin, job["name"])
    runPad.clear()

    # loop through source files/directories to be backed-up
    sources = job["source"].split(":")                   
    for src in sources:

        dateTimeStamp = datetime.now().strftime("%Y%m%d-%H%M%S")  
        
        # check file/directory exists
        if not os.path.exists(src):
            errorProcessing(False, "FAILURE " + dateTimeStamp + " Source file/directory: " + src + " does not exist", dateTimeStamp, True, runPad)
        
        else:
            
            # get destination directory and check it exists
            srcPath = pathlib.PurePath(src)
            
            if not os.path.exists(backupDir):
                errorProcessing(False, "FAILURE " + dateTimeStamp + " Destination directory: " + backupDir + " does not exist", dateTimeStamp, True, runPad)
                
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
                errorProcessing(True, "SUCCESS " + dateTimeStamp + " Backed-up " + src + " to " + dst, dateTimeStamp, True, runPad)

def maintainBackups(stdScr):
    global saved
    global dateTimeStamp
    
    curses.init_pair(YELLOWBLACK, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(BLUEBLACK, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(GREENBLACK, curses.COLOR_GREEN, curses.COLOR_BLACK)
    stdScr = curses.initscr()
    stdScr.leaveok(True)
    rows, cols = getDims(stdScr, False)
    
    showPage(stdScr, rows, cols)
 
    backupDir, jobs = loadBackups() 
    
    backupWin = curses.newwin(1, cols - 20, 1, 20)
    backupText = curses.textpad.Textbox(backupWin, insert_mode = True)
    
    dispWin = curses.newwin(1, cols, rows - 1, 0) 
   
    jobWin = curses.newwin(rows - 2, cols, 1, 0) 
    jobnameWin = curses.newwin(1, 10, 2, 0)
    jobnameText = curses.textpad.Textbox(jobnameWin, insert_mode = True)
    sourceWin = curses.newwin(2, cols - 1, 4, 0)
    sourceText = curses.textpad.Textbox(sourceWin, insert_mode = True)
  
    runWin = curses.newwin(rows - 2, cols, 1, 0) 
    runPad = curses.newpad(100, cols) 
    
    firstRow = 0
    lastRow = len(jobs)
    jobsList = curses.newpad(100, 100)
    
    showBackupDir(backupWin, backupDir)
    
    listBackups(jobs, jobsList, rows, cols, firstRow)
    
    hideCursor(dispWin)
  
    while True: 
        key = stdScr.getch()
        
        if key in keyList(['b']):
            backupDir = setBackupDir(backupWin, backupText)
            saved = False
        elif key in keyList(['a']):
            addBackup(jobWin, dispWin, jobnameWin, jobnameText, sourceWin, sourceText, jobs)
            lastRow += 1
            showPage(stdScr, rows, cols)
            showBackupDir(backupWin, backupDir)
            listBackups(jobs, jobsList, rows, cols, firstRow)    
            saved = False
        elif key in keyList(['r', 'v', 'c', 'd']):
            jobNumber = getIntInput(dispWin, "Job number: ", len(str(len(jobs))))
            if (jobNumber < 1) or (jobNumber > len(jobs)):
                showMessage(dispWin, "Invalid job number.")
            else:
                if key in keyList(['r']):
                    runBackup(runWin, runPad, jobs[jobNumber - 1], backupDir)
                    runPad.refresh(0, 0, 2, 0, rows - 3, cols - 1)
                    showMessage(dispWin, "Press any key to continue.", False)
                    stdScr.getch()
                if key in keyList(['v']):
                    viewBackup(jobWin, dispWin, jobnameWin, sourceWin, jobs[jobNumber - 1])
                    showMessage(dispWin, "Press any key to continue.", False)
                    stdScr.getch()
                if key in keyList(['c']):
                    changeBackup(jobWin, dispWin, jobnameWin, jobnameText, sourceWin, sourceText, jobs[jobNumber - 1])
                    saved = False
                if key in keyList(['d']):
                    viewBackup(jobWin, dispWin, jobnameWin, sourceWin, jobs[jobNumber - 1])
                    showMessage(dispWin, "Delete this job Y/N?", False)
                    key = stdScr.getch()
                    if key in keyList(['y']):
                        jobs.pop(jobNumber - 1)
                        lastRow = len(jobs)
                        saved = False
                showPage(stdScr, rows, cols)
                showBackupDir(backupWin, backupDir)
                listBackups(jobs, jobsList, rows, cols, firstRow)
        elif (key == curses.KEY_DOWN) and (firstRow < lastRow - 1):
            firstRow += 1
            listBackups(jobs, jobsList, rows, cols, firstRow)
        elif (key == curses.KEY_UP) and (firstRow > 0):
            firstRow -= 1
            listBackups(jobs, jobsList, rows, cols, firstRow)
        elif key in keyList(['s']):
            saveBackups(backupDir, jobs)
            showMessage(dispWin, "Backup jobs saved.")
            saved = True
        elif key in keyList(['x']):
            if not saved:
                showMessage(dispWin, "Backups not saved. Save Y/N?", False)
                key = stdScr.getch()
                if key in keyList(['y']):
                    saveBackups(backupDir, jobs)
                    showMessage(dispWin, "Backup jobs saved.")
                    saved = True
            break
        hideCursor(dispWin)
             
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
        global dateTimeStamp
        dateTimeStamp = datetime.now().strftime("%Y%m%d-%H%M%S")  
        
        # check for job name as command line argument
        # error condition
        if len(sys.argv) > 2:
            print("Usage: backups.py JOB  # immediate mode, run JOB\n       backups.py      # maintenance mode, maintain all jobs", file = sys.stderr)
            
        # enter backups maintenance mode
        elif len(sys.argv) == 1:
            wrapper(maintainBackups)
        
        # process job from command line    
        else:
            
            # get job name from command line and check it is included
            # in jobs dictionary
            jobName = sys.argv[1]
            
            if not jobName in jobs:
                errorProcessing(False, "Job: " + jobName + " not found", dateTimeStamp)
            
            else:
                
                # loop through source files/directories to be backed-up
                for src in jobs[jobName]:
                
                    # check file/directory exists
                    if not os.path.exists(src):
                        errorProcessing(False, "Source file/directory: " + src + " does not exist", dateTimeStamp)
                    
                    else:
                        
                        # get destination directory and check it exists
                        srcPath = pathlib.PurePath(src)
                        
                        if not os.path.exists(backupDir):
                            errorProcessing(False, "Destination directory: " + backupDir + " does not exist", dateTimeStamp)
                            
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
                            errorProcessing(True, "Backed-up " + src + " to " + dst, dateTimeStamp)
    
    except Exception as e:
        print("ERROR: backups.py program failed: " + str(e))
  
## call main function  
if __name__ == "__main__":
    main()