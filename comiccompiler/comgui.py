import tkinter as tk
import sys
import os
import webbrowser

from tkinter import filedialog, simpledialog
from tkinter import font
from concurrent import futures

from . import profiles
from . import arguments
from . import compiler
from . import logger

REDIRECT_LOGS = True

thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    if os.path.exists(path):
        return path
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "../" + relative_path)


def input_list(entry, items):
    entry.delete(0, tk.END)
    if items is not None:
        entry.insert(0, " ".join(map(lambda item: trim_and_quote(item), items)))


def extract_list(entry):
    return entry.get().split(" ")


class MainWindow(tk.Frame):
    output_terminal = None
    argument_input = None
    current_thread = None

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.master.iconbitmap(default=resource_path('resources' + os.sep + 'pow_icon.ico'))
        self.master.title("Comic Compiler v1.2.1 (by bajuwa)")
        self.master.resizable(False, False)
        self.grid_columnconfigure(1, weight=1)
        self.grid(pady=3, padx=3)

        self.info_profiles_frame = InfoAndProfilesFrame(self.get_args, self.populate_args_from_text, master)
        self.info_profiles_frame.grid(columnspan=2, row=0, sticky="we", pady=3, padx=3)

        self.input_frame = InputFrame(master)
        self.input_frame.grid(columnspan=2, row=1, sticky="we", pady=3, padx=3)

        self.output_frame = OutputFrame(master)
        self.output_frame.grid(columnspan=2, row=2, sticky="we", pady=3, padx=3)

        self.page_config_frame = PageConfigFrame(master)
        self.page_config_frame.grid(column=0, row=3, sticky="we", pady=3, padx=3)

        self.breakpoint_config_frame = BreakpointConfigFrame(master)
        self.breakpoint_config_frame.grid(column=0, row=4, sticky="we", pady=3, padx=3)

        self.run_frame = RunFrame(self._run_on_thread, master)
        self.run_frame.grid(column=0, row=5, sticky="we", pady=3, padx=3)

        self.logging_frame = LoggingFrame(master)
        self.logging_frame.grid(column=1, row=3, rowspan=6, sticky="nwse", pady=3, padx=3)

    def populate_args_from_text(self, args):
        self.populate_args(arguments.parse(args))

    def preload_with_sys_vars(self):
        self.info_profiles_frame.clear_profile_selection()
        if len(sys.argv) > 1:
            self.populate_args(arguments.parse())

    def populate_args(self, args):
        self.input_frame.populate_args(args)
        self.output_frame.populate_args(args)
        self.page_config_frame.populate_args(args)
        self.breakpoint_config_frame.populate_args(args)
        self.run_frame.populate_args(args)

    def get_args(self):
        text_to_run = ""

        text_to_run += self.input_frame.get_args()
        text_to_run += self.output_frame.get_args()
        text_to_run += self.page_config_frame.get_args()
        text_to_run += self.breakpoint_config_frame.get_args()
        text_to_run += self.run_frame.get_args()

        return text_to_run.strip()

    def _run_on_thread(self):
        if self.current_thread is None or self.current_thread.done():
            self.current_thread = thread_pool_executor.submit(self._run)
            self.current_thread.add_done_callback(self.run_frame.finished_running)
            self.run_frame.started_running()
        else:
            # This doesn't actually cancel.... 
            self.current_thread.cancel()
            if self.current_thread.done():
                self.run_frame.finished_running()

    def _run(self):
        try:
            if self.input_frame.input_files.get() == "":
                logger.error("Must select input files or directory")
                return

            self._run_and_log(self.get_args())
        except:
            print("Unexpected error:", sys.exc_info())
        pass

    def _run_and_log(self, compiler_args):
        self.logging_frame.clear_log()
        logger.debug("Running with arguments: " + compiler_args)
        logger.debug("")
        compiler.run(arguments.parse(compiler_args))


class InfoAndProfilesFrame(tk.Frame):
    def __init__(self, get_args, populate_args_from_text, master=None):
        tk.Frame.__init__(self, master)
        self.grid_columnconfigure(1, weight=1)

        self.get_args = get_args
        self.populate_args_from_text = populate_args_from_text

        tk.Label(self, text="Confused?").grid(row=0, column=0, pady=3, padx=3)
        wiki_link = tk.Label(self, text="Check out the wiki", fg="blue", cursor="hand2", anchor="w")
        wiki_link.grid(row=0, column=1, sticky="we", pady=3, padx=3)
        wiki_link.bind("<Button-1>", lambda e: webbrowser.open_new(
            "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Demo"))

        tk.Label(self, text="Profile:").grid(row=0, column=2, pady=3, padx=3)

        self.profile_options = profiles.get_profile_names()
        self.profile_choice = tk.StringVar(self.master)
        self.profile_choice.trace('w', self.load_profile)
        self.profile_name = tk.OptionMenu(self, self.profile_choice, *self.profile_options)
        self.profile_name.grid(column=3, row=0, pady=3, padx=3)

        button = tk.Button(self, text="Save As...", command=lambda: self.save_profile())
        button.grid(column=4, row=0, pady=3, padx=3)

        button = tk.Button(self, text="Delete", command=lambda: self.delete_profile())
        button.grid(column=5, row=0, pady=3, padx=3)

    def clear_profile_selection(self):
        self.profile_choice.set("Default")

    def set_profile_name(self, profile_name):
        self.profile_choice.set(self.profile_options.index(profile_name))

    def load_profile(self, *args):
        args_text = profiles.load_profile(self.profile_choice.get())
        self.populate_args_from_text(args_text)

    def save_profile(self):
        profile_name = self.prompt_user_for_input(self.profile_choice.get())
        profiles.save_profile(profile_name, self.get_args())
        self.refresh_profiles()
        self.profile_choice.set(profile_name)

    def delete_profile(self):
        profiles.delete_profile(self.profile_choice.get())
        self.profile_options.remove(self.profile_choice.get())
        self.refresh_profiles()
        self.profile_choice.set("Default")

    def refresh_profiles(self):
        self.profile_options = profiles.get_profile_names()
        menu = self.profile_name["menu"]
        menu.delete(0, "end")
        for string in self.profile_options:
            menu.add_command(label=string,
                             command=lambda value=string: self.profile_choice.set(value))

    def prompt_user_for_input(self, default_value):
        return simpledialog.askstring("Save profile as...", "", initialvalue=default_value, parent=self.master)


class InputFrame(tk.LabelFrame):
    def __init__(self, master=None):
        tk.LabelFrame.__init__(self, master, text="Input Files")
        self.grid_columnconfigure(0, weight=1)
        self.input_files = tk.Entry(self)
        self.input_files.grid(row=0, sticky='we', pady=3, padx=3)
        button = tk.Button(self, text="Import From Folder", command=lambda: self.select_directory())
        button.grid(column=1, row=0, pady=3, padx=3)
        button = tk.Button(self, text="Import Files", command=lambda: self.select_files())
        button.grid(column=2, row=0, pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#input-files")\
            .grid(column=3, row=0, pady=3, padx=3)
        pass

    def populate_args(self, args):
        input_list(self.input_files, args.input_files)

    def get_args(self):
        return format_as_argument("-f", extract_list(self.input_files))

    def select_directory(self):
        directory = filedialog.askdirectory(
            title="Select directory to with images to combine..."
        )
        if os.path.isdir(directory):
            self.input_files.delete(0, tk.END)
            self.input_files.insert(0, trim_and_quote(directory + "/*.*"))

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select files to combine..."
        )
        input_list(self.input_files, files)


class OutputFrame(tk.LabelFrame):
    def __init__(self, master=None):
        tk.LabelFrame.__init__(self, master, text="Output Directory")
        self.grid_columnconfigure(0, weight=1)
        self.output_directory = tk.Entry(self)
        self.output_directory.grid(column=0, row=0, sticky='we', pady=3, padx=3)
        button = tk.Button(self, text="Browse", command=lambda: self.select_directory())
        button.grid(column=1, row=0, sticky='we', pady=3, padx=3)
        button.bind('<Return>', lambda e: self.select_directory())
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#output-directory") \
            .grid(column=3, row=0, pady=3, padx=3)

    def populate_args(self, args):
        self.output_directory.delete(0, tk.END)
        if args.output_directory.endswith("/"):
            self.output_directory.insert(0, trim_and_quote(args.output_directory))
        else:
            self.output_directory.insert(0, trim_and_quote(args.output_directory + "/"))

    def get_args(self):
        return format_as_argument("-od", self.output_directory.get())

    def select_directory(self):
        directory = filedialog.askdirectory(
            title="Select directory to output pages to...",
            mustexist=False
        )
        if os.path.isdir(directory):
            self.output_directory.delete(0, tk.END)
            self.output_directory.insert(0, trim_and_quote(directory + "/"))


class PageConfigFrame(tk.LabelFrame):
    def __init__(self, master=None):
        tk.LabelFrame.__init__(self, master, text="Output Pages")
        self.grid_columnconfigure(1, weight=1)

        tk.Label(self, text="Page Names:").grid(row=0, column=0, pady=3, padx=3)
        self.output_file_prefix = tk.Entry(self, width=15, justify='right')
        self.output_file_prefix.grid(row=0, column=1, sticky='we', pady=3, padx=3)
        tk.Label(self, text="###", width=2).grid(row=0, column=2, pady=3, padx=3)
        self.extension = tk.Entry(self, width=5, justify='left')
        self.extension.grid(row=0, column=3, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#output-page-file-prefix") \
            .grid(column=5, row=0, pady=3, padx=3)

        tk.Label(self, text="Starting Number:").grid(row=1, column=0, pady=3, padx=3)
        self.output_file_starting_number = tk.Entry(self)
        self.output_file_starting_number.grid(row=1, column=1, columnspan=3, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#output-page-starting-number") \
            .grid(column=5, row=1, pady=3, padx=3)

        tk.Label(self, text="Page Width:").grid(row=2, column=0, pady=3, padx=3)
        self.output_file_width = tk.Entry(self)
        self.output_file_width.grid(row=2, column=1, columnspan=3, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#output-page-width") \
            .grid(column=5, row=2, pady=3, padx=3)

        tk.Label(self, text="Minimum Height:").grid(row=3, column=0, pady=3, padx=3)
        self.min_height_per_page = tk.Entry(self)
        self.min_height_per_page.grid(row=3, column=1, columnspan=3, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#minimum-height-per-page") \
            .grid(column=5, row=3, pady=3, padx=3)

        tk.Label(self, text="Min Height Last Page:").grid(row=4, column=0, pady=3, padx=3)
        self.min_height_last_page = tk.Entry(self)
        self.min_height_last_page.grid(row=4, column=1, columnspan=3, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#minimum-height-last-page")\
            .grid(column=5, row=4, pady=3, padx=3)
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
        self.min_height_last_page.delete(0, tk.END)
        self.min_height_last_page.insert(0, args.min_height_last_page)

    def get_args(self):
        return \
            format_as_argument("-o", self.output_file_prefix.get()) + \
            format_as_argument("-e", self.extension.get()) + \
            format_as_argument("-osn", self.output_file_starting_number.get()) + \
            format_as_argument("-ow", self.output_file_width.get()) + \
            format_as_argument("-m", self.min_height_per_page.get()) + \
            format_as_argument("-M", self.min_height_last_page.get())


class BreakpointConfigFrame(tk.LabelFrame):
    colour_options_map = {
        "Solid Black/White": ["0 65535", "0", "0"],
        "Any Solid Colour": ["0", "65535", "0"],
        "Non-solid B/W": ["0 65535", "10000", "1000"],
        "Non-solid Colour": ["0", "65535", "1000"]
    }

    def __init__(self, master=None):
        tk.LabelFrame.__init__(self, master, text="Breakpoints")
        self.grid_columnconfigure(1, weight=1)

        tk.Label(self, text="Breakpoint Mode:").grid(row=0, column=0, pady=3, padx=3)
        self.breakpoint_options = ["Let Comicom Decide", "End of File", "Dynamic Search"]
        self.breakpoint_choice = tk.StringVar(self.master)
        self.breakpoint_choice.set(self.breakpoint_options[0])
        self.breakpoint_detection_mode = tk.OptionMenu(self, self.breakpoint_choice, *self.breakpoint_options)
        self.breakpoint_detection_mode.grid(row=0, column=1, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#breakpoint-detection-mode") \
            .grid(column=3, row=0, pady=3, padx=3)

        tk.Label(self, text="Breakpoint Buffer:").grid(row=1, column=0, pady=3, padx=3)
        self.breakpoint_buffer = tk.Entry(self)
        self.breakpoint_buffer.grid(row=1, column=1, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#breakpoint-buffer") \
            .grid(column=3, row=1, pady=3, padx=3)

        tk.Label(self, text="Colour Presets:").grid(row=2, column=0, pady=3, padx=3)
        self.colour_options = [""]
        self.colour_options += self.colour_options_map.keys()
        self.colour_choice = tk.StringVar(self.master)
        self.colour_choice.set(self.colour_options[0])
        self.colour_choice.trace('w', self.load_colour_preset)
        self.colour_preset = tk.OptionMenu(self, self.colour_choice, *self.colour_options)
        self.colour_preset.grid(row=2, column=1, sticky='we', pady=3, padx=3)

        tk.Label(self, text="Split on Colours:").grid(row=3, column=0, pady=3, padx=3)
        self.split_on_colour = tk.Entry(self)
        self.split_on_colour.grid(row=3, column=1, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#split-pages-on-colours") \
            .grid(column=3, row=3, pady=3, padx=3)

        tk.Label(self, text="Error Tolerance:").grid(row=4, column=0, pady=3, padx=3)
        self.colour_error_tolerance = tk.Entry(self)
        self.colour_error_tolerance.grid(row=4, column=1, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#colour-split-error-tolerance") \
            .grid(column=3, row=4, pady=3, padx=3)

        tk.Label(self, text="Standard Deviation:").grid(row=5, column=0, pady=3, padx=3)
        self.colour_standard_deviation = tk.Entry(self)
        self.colour_standard_deviation.grid(row=5, column=1, sticky='we', pady=3, padx=3)
        WikiIcon(self, "https://github.com/bajuwa/ComicCompiler/wiki/Tutorial:-Input-Arguments#colour-split-standard-deviation") \
            .grid(column=3, row=5, pady=3, padx=3)
        pass

    def load_colour_preset(self, *args):
        self.split_on_colour.delete(0, tk.END)
        self.split_on_colour.insert(0, self.colour_options_map[self.colour_choice.get()][0])
        self.colour_error_tolerance.delete(0, tk.END)
        self.colour_error_tolerance.insert(0, self.colour_options_map[self.colour_choice.get()][1])
        self.colour_standard_deviation.delete(0, tk.END)
        self.colour_standard_deviation.insert(0, self.colour_options_map[self.colour_choice.get()][2])

    def populate_args(self, args):
        self.breakpoint_choice.set(self.breakpoint_options[args.breakpoint_detection_mode + 1])
        self.breakpoint_buffer.delete(0, tk.END)
        self.breakpoint_buffer.insert(0, args.breakpoint_buffer)
        self.split_on_colour.delete(0, tk.END)
        self.split_on_colour.insert(0, " ".join(map(lambda c: str(c), args.split_on_colour)))
        self.colour_error_tolerance.delete(0, tk.END)
        self.colour_error_tolerance.insert(0, args.colour_error_tolerance)
        self.colour_standard_deviation.delete(0, tk.END)
        self.colour_standard_deviation.insert(0, args.colour_standard_deviation)

    def get_args(self):
        return format_as_argument("-b", self.breakpoint_options.index(self.breakpoint_choice.get()) - 1) + \
            format_as_argument("-bb", self.breakpoint_buffer.get()) + \
            format_as_argument("-c", self.split_on_colour.get()) + \
            format_as_argument("-ce", self.colour_error_tolerance.get()) + \
            format_as_argument("-csd", self.colour_standard_deviation.get())


class RunFrame(tk.LabelFrame):
    def __init__(self, submit_func, master):
        tk.LabelFrame.__init__(self, master, text="Run")
        self.grid_columnconfigure(3, weight=1)

        self.will_sort_input = tk.BooleanVar()
        self.sort_input = tk.Checkbutton(self, text="Sort input files before stitching", variable=self.will_sort_input,
                                         anchor="w")
        self.sort_input.grid(column=0, row=0, columnspan=4, sticky='we', pady=3, padx=3)

        self.will_check_stitching = tk.BooleanVar()
        self.check_stitching = tk.Checkbutton(self, text="Abort if edges between input images do not match"
                                              , variable=self.will_check_stitching, anchor="w")
        self.check_stitching.grid(column=0, row=1, columnspan=4, sticky='we', pady=3, padx=3)

        self.is_clean = tk.BooleanVar()
        self.clean = tk.Checkbutton(self, text="Clean", variable=self.is_clean)
        self.clean.grid(column=0, row=2, sticky='we', pady=3, padx=3)

        self.is_open = tk.BooleanVar()
        self.open = tk.Checkbutton(self, text="Open", variable=self.is_open)
        self.open.grid(column=1, row=2, sticky='we', pady=3, padx=3)

        self.logging_options = ["Error", "Info", "Warn", "Debug", "Verbose"]
        self.logging_choice = tk.StringVar(self.master)
        self.logging_choice.set(self.logging_options[0])
        self.logging_level = tk.OptionMenu(self, self.logging_choice, *self.logging_options)
        self.logging_level.grid(column=2, row=2, sticky='we', pady=3, padx=3)

        self.run_button_text = tk.StringVar()
        self.run_button_text.set("Run")
        self.run_button = tk.Button(self, textvariable=self.run_button_text, command=lambda: submit_func(),
                               font=font.Font(family='Helvetica', size=10, weight=font.BOLD))
        self.run_button.grid(column=3, row=2, sticky='we', pady=3, padx=3)
        self.run_button.bind('<Return>', lambda e: submit_func())

    def started_running(self):
        #self.run_button_text.set("Cancel")
        self.run_button.config(state="disabled")

    def finished_running(self, *args):
        #self.run_button_text.set("Run")
        self.run_button.config(state="active")

    def populate_args(self, args):
        self.logging_choice.set(self.logging_options[args.logging_level])
        self.will_sort_input.set(not args.disable_input_sort)
        self.will_check_stitching.set(args.enable_stitch_check)
        self.is_open.set(args.open)
        self.is_clean.set(args.clean)

    def get_args(self):
        return format_as_argument("--clean", self.is_clean.get()) + \
               format_as_argument("--open", self.is_open.get()) + \
               format_as_argument("--disable-input-sort", not self.will_sort_input.get()) + \
               format_as_argument("--enable-stitch-check", self.will_check_stitching.get()) + \
               format_as_argument("--logging-level", self.logging_options.index(self.logging_choice.get()))


class LoggingFrame(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        # show the program output when run
        self.grid_rowconfigure(0, weight=1)
        self.output_terminal = tk.Text(self, width=60)
        self.output_terminal.grid(sticky="nesw", pady=3, padx=3)
        self.output_terminal.configure(state='disabled')
        if REDIRECT_LOGS:
            sys.stdout = StdoutRedirector(self.output_terminal)
            sys.stderr = StdoutRedirector(self.output_terminal)
        pass

    def clear_log(self):
        self.output_terminal.configure(state='normal')
        self.output_terminal.delete('1.0', tk.END)
        self.output_terminal.configure(state='disabled')


class WikiIcon(tk.Label):
    def __init__(self, master, wiki_url):
        tk.Label.__init__(self, master, text="ⓘ", fg="blue", cursor="hand2")
        self.bind("<Button-1>", lambda e: webbrowser.open_new(wiki_url))


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


def trim_and_quote(item):
    string = str(item).strip()
    if " " in string:
        return '"' + string + '"'
    return string


def format_as_argument(tag, arg):
    # Beware of issue #16 where spaces in file names cause problems on input
    if arg is not None:
        if isinstance(arg, list):
            return " " + tag + " " + " ".join(list(map(lambda item: trim_and_quote(item), arg)))
        if isinstance(arg, bool):
            if arg:
                return " " + tag
        elif arg != "":
            return " " + str(tag) + ' ' + str(arg)
    return ""
