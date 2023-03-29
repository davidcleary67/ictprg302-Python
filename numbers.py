#!/usr/bin/python3

import math

def main():
    try:
        number = int(input("Enter a number: "))
        
        for n in range(1, number + 1):
            print("The number is " + str(n) + ", its square is " + str(int(math.pow(n , 2))) + " and its cube is " + str(int(math.pow(n, 3))) + ".")
            
    except ValueError:
        print("ERROR: The value entered must be an integer.")
        quit()

if __name__ == '__main__':
    main()
