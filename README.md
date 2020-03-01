# ComicCompiler
Given a set of images, vertically combines them in to 'pages' where the start/end of the page are solid white (or some other specified colour).

## Installation
1. Install ImageMagick and make sure it's added to your PATH: https://imagemagick.org/script/download.php
2. Download the **comcom** file and put it in either:
     1. The directory you want to use it in, or;
     2. In any location on your computer and add that location to your PATH
  
## Command Line Arguments
The arguments for **comcom** are all optional, and if left unspecified they will use the defaults specified below.  

### Minimum Height Per Page
**Shorthand:** -h [number]  
**Longhand:** --min-height-per-page [number]  
**Default:** 5000  
The minimum allowed pixel height per page.  When combining images, the script will not start looking for 'whitespace' until it has first hit this height requirement.

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

### Output Directory
**Shorthand:** -od [text]   
**Longhand:** --output-directory [text]   
**Default:** "./"  
The path to the directory you want to put the new page files in. By default it's set to "./" which refers to your **current working directory**, aka the location you're in when you run the script.

### Whitespace Break Mode
**Shorthand:** -m [number]   
**Longhand:** --whitespace-break-mode [number]   
**Default:** 0  
The "mode" that the script uses to detect where to split up pages.
**Mode 0:** This is the simplest mode and runs in just a few seconds. After reaching your specified **Minimum Page Height** requirement, it will then keep adding images to the page until it adds an image the *ends in a single line of whitespace*. This means that if your series of images often split panels across images, you will likely generate randomly long page files.  If that's the case, then use mode 1 instead.
**Mode 1:** This is a more complex algorithm that takes quite a bit longer (usually around a minute per chapter depending on input) as it will search the entire image for a breakpoint instead of just the last line of the file.  While this mode takes longer, it often produces more consistent page sizes.

### Break Point Row Check Increments
**Shorthand:** -bi [text]   
**Longhand:** --break-points-increment [number]   
**Default:** 10  
When in **Whitespace Break Mode #1** this value controls how often the script tests a line in an image file for whitespace. Increasing this value will make the script run faster, but may cause smaller whitespace gaps to be missed when trying to split.  Reducing the value will do the opposite: script runs slower but will more reliably detect smaller whitespace gaps between panels.   
**Example:** When running `comcom -m 1 -bi 10` the script will check row 0 for whitespace, then row 10, then row 20, until it either finds whitespace or reaches the end of the file.

### Break Point Row Check Multiplier
**Shorthand:** -bm [text]   
**Longhand:** --break-points-multiplier [number]   
**Default:** 20  
When in **Whitespace Break Mode #1** this value controls how large of a vertical area is pre-tested for *whitespace* before iterating over rows via **Break Point Row Check Increments**.   
**Example:** When running `comcom -m 1 -bi 10 -bm 20` this script will first check a vertical strip down the center of the image that's 200 pixels tall (where bi of 10 times bm of 20 equals 200). If this 200 pixel space doesn't contain any *whitespace* then the script will skip that area and check the next area of 200 pixels. This value can help reduce the number of horizontal rows tested which will reduce script run time.  
**Note:** When increasing/decreasing the **Check Increments** value, consider decreasing/increasing the **Check Multiplier** such that you stay in a range close to 200-300 pixels, otherwise you may lose performance benefits.

### Split Pages on Colour
**Shorthand:** -c [number]   
**Longhand:** --split-on-colour [number]   
**Default:** 65535 (white)  
The decimal notation of the colour you want to split on.  Use 65535 for white (which is the default) or 0 for black. For this set of documentation any reference to *whitespace* will actually refer to the colour specified here, not necessarily 'white'.

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
