#!/usr/bin/python3

def main():
    """
    This Python code demonstrates the following features:
    
    * opening, writing and closing a text file.
    
    """
    try:
        file = open("dir1/file1.txt", "a")
        
        file.write("FAILURE unknown job.\n")
        file.write("FAILURE source file did not exist.\n")
        file.write("SUCCESS backup completed.\n")
        
        file.close()
    
    except FileNotFoundError:
        print("ERROR: File does not exist.")
   
    except IOError:
        print("ERROR: File is not accessible.")
    
if __name__ == "__main__":
    main()