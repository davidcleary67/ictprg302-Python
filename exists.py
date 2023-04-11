#!/usr/bin/python3

import sys
import os

def main():
    """
    This Python code demonstrates the following features:
    
    * checking that a file or directory exists.
    
    """
    try:
        fileExists = "/home/ec2-user/environment/ictprg302-2023S1/cli.py"
        fileNotExists = "/home/ec2-user/environment/ictprg302-2023S1/xxx.py"
        
        if not os.path.exists(fileExists):
            print("ERROR: file " + fileExists + " does not exist.")
        else:
            print("ERROR: file " + fileExists + " does exist.")
            
        if not os.path.exists(fileNotExists):
            print("ERROR: file " + fileNotExists + " does not exist.")
        else:
            print("ERROR: file " + fileNotExists + " does exist.")
            
    except:
        print("ERROR: An error occurred.")
    
if __name__ == "__main__":
    main()