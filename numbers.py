#!/usr/bin/python3

def main():
    try:
        number = int(input("Enter a number: "))
        
        for n in range(1, number + 1):
            print("The numbe is " + str(n))
            
    except ValueError:
        print("ERROR: The value entered must be an integer.")
        quit()

if __name__ == '__main__':
    main()
