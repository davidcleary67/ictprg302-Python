#!/usr/bin/python3

import curses
from curses import wrapper
from curses.textpad import Textbox, rectangle

def showDims(win):
    win.addstr(f"Lines: {curses.LINES}, Rows: {curses.COLS}\n")
    win.refresh()
    win.addstr("Press any key to continue.")
    win.getch()

def maintainbackups(stdScr):
    stdScr = curses.initscr()
    showDims(stdScr)
    stdScr.clear()
   
    """
    inpWin = curses.newwin(1, 1, curses.LINES - 1, curses.COLS - 1) 
    inpWin.clear()
    inpWin.refresh()
    
    name = getInput(inpWin, 1, 1, "Name: ")
    inpWin.addstr(name)
    inpWin.refresh()
    
    """
    stdScr.getch()
    
    curses.endwin()