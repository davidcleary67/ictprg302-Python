#!/usr/bin/python3

import sys
import pathlib
import shutil
from datetime import datetime

def main():
    """
    This Python code demonstrates the following features:
    
    * extracting the path component from a full file specification
    * copying a file
    * copying a directory.
    
    """
    try:
        dateTimeStamp = datetime.now().strftime("%Y%m%d-%H%M%S")  
        
        srcFile = "/home/ec2-user/environment/ictprg302-2023S1/file1.txt"
        srcDir = "/home/ec2-user/environment/ictprg302-2023S1/dir1"
        
        srcLoc = srcDir# change this srcLoc = srcDir to test copying a directory
        srcPath = pathlib.PurePath(srcLoc)
        
        dstDir = "/home/ec2-user/environment/ictprg302-2023S1/backups"
        dstLoc = dstDir + "/" + srcPath.name + "-" + dateTimeStamp
        
        print("Date time stamp is " + dateTimeStamp) 
        print("Source file is " + srcFile)
        print("Source directory is " + srcDir)
        print("Source location is " + srcLoc)
        print("Destination directory is " + dstDir)
        print("Destination location is " + dstLoc)
        
        if pathlib.Path(srcLoc).is_dir():4yy
            shutil.copytree(srcLoc, dstLoc)
        else:
            shutil.copy2(srcLoc, dstLoc)
    except:
        print("ERROR: An error occurred.")
    
if __name__ == "__main__":
    main()