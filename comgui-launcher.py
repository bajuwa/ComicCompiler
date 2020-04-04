#!/usr/bin/env python

import tkinter

from comiccompiler import comgui
from comiccompiler import arguments


# execute only if run as a script
if __name__ == "__main__":
    window = tkinter.Tk()
    comgui = comgui.MainWindow(window)
    comgui.populate_args(arguments.parse())
    window.mainloop()
