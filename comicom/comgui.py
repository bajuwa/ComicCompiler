import tkinter as tk
import sys

from . import arguments
from . import compiler
from . import logger


class MainWindow(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.init_window()

    def init_window(self):
        # changing the title of our master widget
        self.master.title("Comic Compiler")
        self.grid_columnconfigure(0, weight=1)

        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        # allow user to input arguments
        tk.Label(self, text="Input your command line arguments here then press 'run'")\
            .grid(sticky='w')
        argument_input = tk.Entry(self)
        argument_input.grid(column=0, row=1, sticky='we')
        argument_input.focus()

        # show the program output when run
        output_terminal = tk.Text(self)
        output_terminal.grid(columnspan=2, row=2, sticky="we")
        output_terminal.configure(state='disabled')
        sys.stdout = StdoutRedirector(output_terminal)
        sys.stderr = StdoutRedirector(output_terminal)

        # creating a button instance
        tk.Button(self, text="Run", command=lambda: run_and_log(output_terminal, argument_input.get())) \
            .grid(column=1, row=1)

    def preload_args(self, text_arguments=None):
        # if text_arguments == "":
        #     text_arguments = None
        # args = arguments.parse(text_arguments)
        pass


def run_and_log(output_terminal, argument_input):
    output_terminal.configure(state='normal')
    output_terminal.delete('1.0', tk.END)
    output_terminal.configure(state='disabled')
    try:
        if argument_input == "":
            argument_input = None
        compiler.run(arguments.parse(argument_input))
    except:
        print("Unexpected error:", sys.exc_info()[0])
    pass


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.configure(state='normal')
        self.text_space.insert('end', string.replace(logger.delete_line_string, "\n"))
        self.text_space.see('end')
        self.text_space.configure(state='disabled')

    def flush(self):
        self.text_space.update_idletasks()
