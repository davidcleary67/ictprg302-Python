#!/usr/bin/python3

from datetime import datetime

def main():
    """
    This Python code demonstrates the following features:
    
    * creating a datetime stamp.
    
    """
    try:
        dateTimeStamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        print(dateTimeStamp)
        print("The current date and time is " + dateTimeStamp + ".")
    except:
        print("ERROR: An error occurred.")
    
if __name__ == "__main__":
    main()