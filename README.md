# ComicCompiler
Given a set of images, vertically combines them in to 'pages' where the start/end of the page are solid white (or some other specified colour).

A small demo can be seen here, or you can [view all demos](https://github.com/bajuwa/ComicCompiler/blob/master/demos/):   
![ComCom demo](https://github.com/bajuwa/ComicCompiler/blob/master/demos/simple.gif)

## Installation
1. Make sure you can run shell scripts. Generally speaking you have 2 options:
     1. Use a command line terminal replacement like Git Bash (https://git-scm.com/downloads) (this is what I've been using)
     2. On Windows 10 you can activate WSL and install a distro of your choice, more info: https://docs.microsoft.com/en-us/windows/wsl/install-win10
2. Install ImageMagick (Version 6 or 7): https://imagemagick.org/script/download.php
     1. When installing, an option to 'add to path' should already be selected for you. This is required so don't uncheck it!
3. Download the **comcom** file to any location you want, but make sure to add that location to your PATH
  
## Tutorial 
#### Running ComCom
1. To get started, make sure all your image files are in a single folder on your computer.
      1. For this example, we'll assume your images are all named something like `image001.jpg`.  If this isn't the case, see the [Common Problems](#common-problems) section.
2. Open up that folder in your command line.
3. Run the main `comcom` command (no additional arguments necessary)
4. At this point, you'll see information printed to your screen.  If all goes well you should see something like `Starting compilation...`.
5. Once the script is done, it will say something like `Compilation Complete` and will stop.  You can then open up the new `./Compiled/` folder in your current directory and see the pages that were generated.
      1. If the pages don't look as you want them, then you'll have to add arguments to adjust the behaviour.  Below in are some common examples, but you can see a complete list in the [Command Line Arguments](#command-line-arguments) section.

#### Common Problems       
- Page heights are inconsistent   
       - Try changing the [Breakpoint Mode Detection](#breakpoint-detection-mode) via  `-m 1`
- Pages are too short  
       - Increase the [Minimum Height Per Page](#minimum-height-per-page) 
- My images aren't named `image001.jpg` / Error: "Cannot find any images"  
       - Change the [Input File Name Prefix](#input-file-name-prefix)
       - You can also ignore input file prefix via `-i ""` if you know all the files in the directory are supposed to be included 

## Command Line Arguments
The arguments for **comcom** are all optional, and if left unspecified they will use the defaults specified below.  

### Minimum Height Per Page
**Shorthand:** -h [number]  
**Longhand:** --min-height-per-page [number]  
**Default:** 5000  
The minimum allowed pixel height per page.  When combining images, the script will not start looking for a breakpoint until it has first hit this height requirement.

### Input File Name Prefix
**Shorthand:** -i [text]   
**Longhand:** --input-file-prefix [text]  
**Default:** "image"  
Will only combine images that start with this text.  
**Example:** if a directory contains image001.jpg image002.jpg and test.jpg, and you run `comcom -i image`, only image001.jpg and image002.jpg will be combine in to the final page file.

### File Extension
**Shorthand:** -e [text]   
**Longhand:** --extension [text]   
**Default:** ".jpg"  
The file extension of your input images and your output page files. This value is also included in the initial file selection pattern.  
**Example:** if a directory contains image001.jpg image002.jpg and image003.png, and you run `comcom -e jpg`, only image001.jpg and image002.jpg will be combine in to the final page000.jpg file (the png file will be excluded).

### Output Page File Prefix
**Shorthand:** -o [text]   
**Longhand:** --output-file-prefix [text]   
**Default:** "page"  
The text that will go at the start of each output page name. The prefix is followed by a 3 digit number (zero-padded page number) and the **File Extension** that was set that matches the input image file types.

### Input Directory
**Shorthand:** -id [text]   
**Longhand:** --input-directory [text]   
**Default:** "./"  
The path to the directory you want to collect image files from. By default it's set to "./" which refers to your **current working directory**, aka the location you're in when you run the script.

### Include Subdirectories
**Shorthand:** -is   
**Longhand:** --include-sub-directories   
**Default:** false  
This will include images in subdirectories.   
**Example:** If there is ./chapter1/image1/image01.jpg and ./chapter1/image2/image02.jpg and you're using the input directory ./chapter1 then, by default, neither image will be found. Enabling this will include both images assuming they match the prefix pattern and file extensions. 

### Output Directory
**Shorthand:** -od [text]   
**Longhand:** --output-directory [text]   
**Default:** "./Compiled/"  
The path to the directory you want to put the new page files in. By default it's set to "./Compiled/" which will create a new folder called 'Compiled' in your **current working directory**, aka the location you're in when you run the script, and put your generated pages in that folder.

### Breakpoint Detection Mode
**Shorthand:** -m [number]   
**Longhand:** --breakpoint-detection-mode [number]   
**Default:** 0  
The "mode" that the script uses to detect where to split up pages. In general, the script will continue to combine images until it  reaches your specified **Minimum Page Height** requirement. After that requirement is hit, it will then start looking for breakpoints. This mode setting controls how the script tries to find these breakpoints.   
**Mode 0:** This is the simplest mode and runs the fastest. It will try to break pages when it adds an image that *ends in a single line of the breakpoint colour*. This means that if your series of images often split panels across images, you will likely generate randomly long page files.  If that's the case, then use mode 1 instead.   
**Mode 1:** This is a more complex algorithm that could take a bit longer as it may need to search the entire image for a breakpoint instead of just the last line of the file.  While this mode takes longer, it often produces more consistent page sizes as it can better handle long unbroken panels or images that don't neatly cut between panels.   

### Breakpoint Row Check Increments
**Shorthand:** -bi [text]   
**Longhand:** --break-points-increment [number]   
**Default:** 10  
When in **Breakpoint Detection Mode #1** this value controls how often the script tests a line in an image file for a breakpoint. Increasing this value will make the script run faster, but may cause smaller gaps to be missed when trying to split.  Reducing the value will do the opposite: script runs slower but will more reliably detect smaller gaps between panels.   
**Example:** When running `comcom -m 1 -bi 10` the script will check row 0 for a breakpoint, then row 10, then row 20, until it either finds a breakpoint or reaches the end of the file.

### Breakpoint Row Check Multiplier
**Shorthand:** -bm [text]   
**Longhand:** --break-points-multiplier [number]   
**Default:** 20  
When in **Breakpoint Detection Mode #1** this value controls how large of a vertical area is pre-tested for a breakpoint before iterating over rows via **Breakpoint Row Check Increments**.   
**Example:** When running `comcom -m 1 -bi 10 -bm 20` this script will first check a vertical strip down the center of the image that's 200 pixels tall (where bi of 10 times bm of 20 equals 200). If this 200 pixel space doesn't contain any breakpoints then the script will skip that area and check the next area of 200 pixels. This value can help reduce the number of horizontal rows tested which will reduce script run time.     
**Note:** When increasing/decreasing the **Check Increments** value, consider decreasing/increasing the **Check Multiplier** such that you stay in a range close to 200-300 pixels, otherwise you may lose performance benefits.

### Split Pages on Colour
**Shorthand:** -c [number]   
**Longhand:** --split-on-colour [number]   
**Default:** 65535 (white)  
The decimal notation of the colour you want to split on.  Use 65535 for white (which is the default), 0 for black, or any number in that range for your intended colour.

### Colour Split Error Tolerance
**Shorthand:** -ce [number]   
**Longhand:** --colour-error-tolerance [number]   
**Default:** 0  
If the images aren't always the exact same colour but are often within a range of colours, change this value to allow for more variance in what decimal colour values are 'accepted' to split by.  Regardless of this error tolerance, the entire horizontal line must still be a solid colour. 

### Logging Mode
**Shorthand:** -l [number]   
**Longhand:** --logging-mode [number], --debug, --verbose   
**Default:** 0  
Controls how much text is output to the console while the script is running. Mode 0 only reports the bare minimum of which image range was compiled into which page file.  Mode 1 (aka debug) reports additional info that describes which broad 'decisions' were made during the scripts execution. Mode 2 (aka verbose) will report everything in debug mode as well as specific data values that lead to the script decisions.   
**Example:** `comcom -l 1` is equivalent to `comcom --debug` and `comcom -l 2` is equivalent to `comcom --verbose`

### ImageMagick Version
**Shorthand:** -im6, -im7
**Default:** Version 7  
This flag will allow you to specify a specific version of ImageMagick to use when running **comcom**. By default it uses Version 7 (`-im7`) as that's the most recent version available at the time I write this.  Version 6 is also supported via the `-im6` flag.
