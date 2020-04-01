import tkinter as tk
import webbrowser
import sys

from . import arguments
from . import compiler
from . import logger


command_line_documentation = "https://github.com/bajuwa/ComicCompiler/wiki/ComCom-(" \
                             "Python-Version)#command-line-arguments "


class MainWindow(tk.Frame):
    output_terminal = None
    argument_input = None

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title("Comic Compiler")
        self.grid_columnconfigure(0, weight=1)

        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=1)

        # allow user to input arguments
        tk.Label(self, text="Input your command line arguments here then press 'run'") \
            .grid(column=0, row=0, sticky='w', pady=5, padx=5)

        wiki_link = tk.Label(self, text="more info", fg="blue", cursor="hand2")
        wiki_link.grid(column=1, row=0, sticky='w', pady=5, padx=5)
        wiki_link.bind("<Button-1>", lambda e: webbrowser.open_new(command_line_documentation))

        self.argument_input = tk.Entry(self)
        self.argument_input.grid(column=0, row=1, sticky='we', pady=5, padx=5)
        self.argument_input.bind('<Return>', lambda e: self.run())
        self.argument_input.focus()

        # show the program output when run
        self.output_terminal = tk.Text(self)
        self.output_terminal.grid(columnspan=2, row=2, sticky="we", pady=5, padx=5)
        self.output_terminal.configure(state='disabled')
        sys.stdout = StdoutRedirector(self.output_terminal)
        sys.stderr = StdoutRedirector(self.output_terminal)

        # creating a button instance
        run_button = tk.Button(self, text="Run", command=lambda: self.run())
        run_button.grid(column=1, row=1, sticky='we', pady=5, padx=5)
        run_button.bind('<Return>', lambda e: self.run())

    def run_and_log(self, text_to_run):
        if self.output_terminal is None:
            return

        self.output_terminal.configure(state='normal')
        self.output_terminal.delete('1.0', tk.END)
        self.output_terminal.configure(state='disabled')
        try:
            if text_to_run == "":
                text_to_run = None
            compiler.run(arguments.parse(text_to_run))
        except:
            print("Unexpected error:", sys.exc_info()[0])
        pass

    def run(self):
        self.run_and_log(self.argument_input.get())


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
