#!/usr/bin/env python

import tkinter

from comiccompiler import comgui


# execute only if run as a script
if __name__ == "__main__":
    window = tkinter.Tk()
    comgui = comgui.MainWindow(window)
    window.mainloop()
