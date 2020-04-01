#!/usr/bin/env python

import tkinter

from comicom import compiler
from comicom import comgui
from comicom import arguments


# execute only if run as a script
if __name__ == "__main__":
    args = arguments.parse()

    # Trigger the actual program....
    if args.gui:
        window = tkinter.Tk()
        comgui = comgui.MainWindow(window)
        window.mainloop()
    else:
        compiler.run(args)
