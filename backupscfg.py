#!/usr/bin/python3

# jobs dictionary
jobs = {"job1" : ["work/file1.txt", "work/file2.txt"],
        "job2" : ["work/dir1"],
        "job3" : ["work/missing.txt"]}

# email settings
smtp = {"sender": "dcleary@sunitafe.edu.au",
        "recipient": "davidcgcleary@gmail.com",
        "server": "smtp.gmail.com",
        "port": 587,
        "user": "davidcgcleary@gmail.com", # need to specify a gmail email address with an app password setup
        "password": "buaytgfwfrxxudme"}    # need a gmail app password     

# backup directory
backupDir = "backups"

# log file
logFile = "backup.log"

