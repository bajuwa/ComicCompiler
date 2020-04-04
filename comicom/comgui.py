import tkinter as tk
import sys
import os

from tkinter import filedialog
from tkinter import font

from . import arguments
from . import compiler
from . import logger

REDIRECT_LOGS = True

command_line_documentation = "https://github.com/bajuwa/ComicCompiler/wiki/ComCom-(" \
                             "Python-Version)#command-line-arguments "


class MainWindow(tk.Frame):
    output_terminal = None
    argument_input = None

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.title("Comic Compiler")
        self.master.resizable(False, False)
        self.grid_columnconfigure(1, weight=1)
        self.grid(pady=5, padx=5)

        self.input_frame = InputFrame(master)
        self.input_frame.grid(columnspan=2, row=0, sticky="we", pady=5, padx=5)

        self.output_frame = OutputFrame(master)
        self.output_frame.grid(columnspan=2, row=1, sticky="we", pady=5, padx=5)

        self.page_config_frame = PageConfigFrame(master)
        self.page_config_frame.grid(column=0, row=2, sticky="we", pady=5, padx=5)

        self.breakpoint_config_frame = BreakpointConfigFrame(master)
        self.breakpoint_config_frame.grid(column=0, row=3, sticky="we", pady=5, padx=5)

        self.run_frame = RunFrame(self._run, master)
        self.run_frame.grid(column=0, row=4, sticky="we", pady=5, padx=5)

        self.logging_frame = LoggingFrame(master)
        self.logging_frame.grid(column=1, row=2, rowspan=6, sticky="nwse", pady=5, padx=5)

    def populate_args(self, args):
        self.input_frame.populate_args(args)
        self.output_frame.populate_args(args)
        self.page_config_frame.populate_args(args)
        self.breakpoint_config_frame.populate_args(args)
        self.run_frame.populate_args(args)

    def _run(self):
        try:
            if self.input_frame.input_files.get() == "":
                logger.info("Error: Must select input files or directory")
                return

            text_to_run = ""

            text_to_run += self.input_frame.get_args()
            text_to_run += self.output_frame.get_args()
            text_to_run += self.page_config_frame.get_args()
            text_to_run += self.breakpoint_config_frame.get_args()
            text_to_run += self.run_frame.get_args()

            self._run_and_log(text_to_run.strip())
        except:
            print("Unexpected error:", sys.exc_info())
        pass

    def _run_and_log(self, compiler_args):
        self.logging_frame.clear_log()
        logger.debug("Running with arguments: " + compiler_args)
        logger.debug("")
        compiler.run(arguments.parse(compiler_args))


class InputFrame(tk.LabelFrame):
    def __init__(self, master=None):
        tk.LabelFrame.__init__(self, master, text="Input Files")
        self.grid_columnconfigure(0, weight=1)
        self.input_files = tk.Entry(self)
        self.input_files.grid(row=0, sticky='we', pady=5, padx=5)
        button = tk.Button(self, text="Import From Folder", command=lambda: self.select_directory())
        button.grid(column=1, row=0, pady=5, padx=5)
        button = tk.Button(self, text="Import Files", command=lambda: self.select_files())
        button.grid(column=2, row=0, pady=5, padx=5)
        pass

    def populate_args(self, args):
        self.input_files.delete(0, tk.END)
        self.input_files.insert(0, " ".join(args.input_files))

    def get_args(self):
        return format_as_argument("-f", self.input_files.get())

    def select_directory(self):
        directory = filedialog.askdirectory(
            title="Select directory to with images to combine..."
        )
        if os.path.isdir(directory):
            self.input_files.delete(0, tk.END)
            self.input_files.insert(0, directory + "/*.*")

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select files to combine..."
        )
        self.input_files.delete(0, tk.END)
        self.input_files.insert(0, files)


class OutputFrame(tk.LabelFrame):
    def __init__(self, master=None):
        tk.LabelFrame.__init__(self, master, text="Output Directory")
        self.grid_columnconfigure(0, weight=1)
        self.output_directory = tk.Entry(self)
        self.output_directory.grid(column=0, row=0, sticky='we', pady=5, padx=5)
        button = tk.Button(self, text="Browse", command=lambda: self.select_directory())
        button.grid(column=1, row=0, sticky='we', pady=5, padx=5)
        button.bind('<Return>', lambda e: self.select_directory())

    def populate_args(self, args):
        self.output_directory.delete(0, tk.END)
        if args.output_directory.endswith("/"):
            self.output_directory.insert(0, args.output_directory)
        else:
            self.output_directory.insert(0, args.output_directory + "/")

    def get_args(self):
        return format_as_argument("-od", self.output_directory.get())

    def select_directory(self):
        directory = filedialog.askdirectory(
            title="Select directory to output pages to...",
            mustexist=False
        )
        if os.path.isdir(directory):
            self.output_directory.delete(0, tk.END)
            self.output_directory.insert(0, directory + "/")


class PageConfigFrame(tk.LabelFrame):
    def __init__(self, master=None):
        tk.LabelFrame.__init__(self, master, text="Output Pages")
        self.grid_columnconfigure(1, weight=1)

        tk.Label(self, text="Page Names:").grid(row=0, column=0, pady=5, padx=5)
        self.output_file_prefix = tk.Entry(self, width=15, justify='right')
        self.output_file_prefix.grid(row=0, column=1, sticky='we', pady=5, padx=5)
        tk.Label(self, text="###", width=2).grid(row=0, column=2, pady=5, padx=5)
        self.extension = tk.Entry(self, width=5, justify='left')
        self.extension.grid(row=0, column=3, sticky='we', pady=5, padx=5)

        tk.Label(self, text="Starting Number:").grid(row=1, column=0, pady=5, padx=5)
        self.output_file_starting_number = tk.Entry(self)
        self.output_file_starting_number.grid(row=1, column=1, columnspan=3, sticky='we', pady=5, padx=5)

        tk.Label(self, text="Page Width:").grid(row=2, column=0, pady=5, padx=5)
        self.output_file_width = tk.Entry(self)
        self.output_file_width.grid(row=2, column=1, columnspan=3, sticky='we', pady=5, padx=5)

        tk.Label(self, text="Minimum Height:").grid(row=3, column=0, pady=5, padx=5)
        self.min_height_per_page = tk.Entry(self)
        self.min_height_per_page.grid(row=3, column=1, columnspan=3, sticky='we', pady=5, padx=5)
        pass

    def populate_args(self, args):
        self.output_file_prefix.delete(0, tk.END)
        self.output_file_prefix.insert(0, args.output_file_prefix)
        self.extension.delete(0, tk.END)
        self.extension.insert(0, args.extension)
        self.output_file_starting_number.delete(0, tk.END)
        self.output_file_starting_number.insert(0, args.output_file_starting_number)
        self.output_file_width.delete(0, tk.END)
        self.output_file_width.insert(0, args.output_file_width)
        self.min_height_per_page.delete(0, tk.END)
        self.min_height_per_page.insert(0, args.min_height_per_page)

    def get_args(self):
        return \
            format_as_argument("-o", self.output_file_prefix.get()) + \
            format_as_argument("-e", self.extension.get()) + \
            format_as_argument("-osn", self.output_file_starting_number.get()) + \
            format_as_argument("-ow", self.output_file_width.get()) + \
            format_as_argument("-m", self.min_height_per_page.get())


class BreakpointConfigFrame(tk.LabelFrame):
    def __init__(self, master=None):
        tk.LabelFrame.__init__(self, master, text="Breakpoints")
        self.grid_columnconfigure(1, weight=1)

        tk.Label(self, text="Breakpoint Mode:").grid(row=0, column=0, pady=5, padx=5)
        self.breakpoint_options = ["End of File", "Dynamic Search"]
        self.breakpoint_choice = tk.StringVar(self.master)
        self.breakpoint_choice.set(self.breakpoint_options[0])
        self.breakpoint_detection_mode = tk.OptionMenu(self, self.breakpoint_choice, *self.breakpoint_options)
        self.breakpoint_detection_mode.grid(row=0, column=1, sticky='we', pady=5, padx=5)

        tk.Label(self, text="Split on Colours:").grid(row=1, column=0, pady=5, padx=5)
        self.split_on_colour = tk.Entry(self)
        self.split_on_colour.grid(row=1, column=1, sticky='we', pady=5, padx=5)

        tk.Label(self, text="Error Tolerance:").grid(row=2, column=0, pady=5, padx=5)
        self.colour_error_tolerance = tk.Entry(self)
        self.colour_error_tolerance.grid(row=2, column=1, sticky='we', pady=5, padx=5)

        tk.Label(self, text="Standard Deviation:").grid(row=3, column=0, pady=5, padx=5)
        self.colour_standard_deviation = tk.Entry(self)
        self.colour_standard_deviation.grid(row=3, column=1, sticky='we', pady=5, padx=5)
        pass

    def populate_args(self, args):
        self.breakpoint_choice.set(self.breakpoint_options[args.breakpoint_detection_mode])
        self.split_on_colour.delete(0, tk.END)
        self.split_on_colour.insert(0, " ".join(map(lambda c: str(c), args.split_on_colour)))
        self.colour_error_tolerance.delete(0, tk.END)
        self.colour_error_tolerance.insert(0, args.colour_error_tolerance)
        self.colour_standard_deviation.delete(0, tk.END)
        self.colour_standard_deviation.insert(0, args.colour_standard_deviation)

    def get_args(self):
        return format_as_argument("-b", self.breakpoint_options.index(self.breakpoint_choice.get())) + \
            format_as_argument("-c", self.split_on_colour.get()) + \
            format_as_argument("-ce", self.colour_error_tolerance.get()) + \
            format_as_argument("-csd", self.colour_standard_deviation.get())


class RunFrame(tk.LabelFrame):
    def __init__(self, submit_func, master=None):
        tk.LabelFrame.__init__(self, master, text="Run")
        self.grid_columnconfigure(1, weight=1)

        self.is_clean = tk.IntVar()
        self.clean = tk.Checkbutton(self, text="Clean", variable=self.is_clean)
        self.clean.grid(column=0, row=0, sticky='we', pady=5, padx=5)

        self.is_open = tk.IntVar()
        self.open = tk.Checkbutton(self, text="Open", variable=self.is_open)
        self.open.grid(column=1, row=0, sticky='we', pady=5, padx=5)

        self.logging_options = ["Info", "Debug", "Verbose"]
        self.logging_choice = tk.StringVar(self.master)
        self.logging_choice.set(self.logging_options[0])
        self.logging_level = tk.OptionMenu(self, self.logging_choice, *self.logging_options)
        self.logging_level.grid(column=2, row=0, sticky='we', pady=5, padx=5)

        self.argument_input = tk.Entry(self)
        self.argument_input.grid(column=0, columnspan=3, row=1, sticky="we", pady=5, padx=5)
        self.argument_input.bind('<Return>', lambda e: submit_func())
        self.argument_input.focus()

        run_button = tk.Button(self, text="Run", command=lambda: submit_func(),
                               font=font.Font(family='Helvetica', size=16, weight=font.BOLD))
        run_button.grid(column=3, row=0, rowspan=2, pady=5, padx=5)
        run_button.bind('<Return>', lambda e: submit_func())
        pass

    def populate_args(self, args):
        self.logging_choice.set(self.logging_options[args.logging_level])
        self.is_open.set(1 if args.open else 0)
        self.is_clean.set(1 if args.clean else 0)

    def get_args(self):
        return self.argument_input.get() + \
            format_bool_as_argument("--clean", self.is_clean.get() == 1) + \
            format_bool_as_argument("--open", self.is_open.get() == 1) + \
            format_as_argument("--logging-level", self.logging_options.index(self.logging_choice.get()))


class LoggingFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        # show the program output when run
        self.output_terminal = tk.Text(self, width=60)
        self.output_terminal.grid(sticky="nesw", pady=5, padx=5)
        self.output_terminal.configure(state='disabled')
        if REDIRECT_LOGS:
            sys.stdout = StdoutRedirector(self.output_terminal)
            sys.stderr = StdoutRedirector(self.output_terminal)
        pass

    def clear_log(self):
        self.output_terminal.configure(state='normal')
        self.output_terminal.delete('1.0', tk.END)
        self.output_terminal.configure(state='disabled')


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


def format_as_argument(tag, arg):
    # Beware of issue #16 where spaces in file names cause problems on input
    if arg != "" and arg is not None:
        return " " + str(tag) + " " + str(arg)
    return ""


def format_list_as_argument(tag, arg_list):
    # Beware of issue #16 where spaces in file names cause problems on input
    if arg_list is not None and len(arg_list) > 0:
        return " " + tag + " " + " ".join(arg_list)
    return ""


def format_bool_as_argument(tag, arg):
    if arg:
        return " " + tag
    return ""


def empty_to_none(param, on_empty):
    if param == "" or param is None:
        return on_empty
    return param
