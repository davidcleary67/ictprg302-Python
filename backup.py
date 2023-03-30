#!/usr/bin/python3

import sys
from backupcfg import jobs

def errorProcessing(errorMessage):
    """ Display error message to the screem, email it to the administrator and
        write it to the log file backup.log.
    """
    print("ERROR: " + errorMessage)

def main():
    """ Main function.  Backup a file or directory referred to by command line
        argument and specified in jobs in the backupcfg.py file.
        Errors are displayed on the screen, emailed to the adminstrator and 
        written to the log file backup.log.
    """
    try:
        # check for job name as command line argument
        if len(sys.argv) != 2:
            errorProcessing("Job name missing")
        else:
            jobName = sys.argv[1]
            
            # check job name is included in jobs dictionary
            if not jobName in jobs:
                errorProcessing("Job not found in dictionary")
            else:
                print(jobs)
    except:
        print("ERROR: Programmed failed")
    
if __name__ == "__main__":
    main()