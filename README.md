# ComicCompiler
Given a set of images, vertically combines them in to 'pages' where the start/end of the page are solid white (or some other specified colour).
For more information on installation and how to use comcom, [see our github wiki](https://github.com/bajuwa/ComicCompiler/wiki).

While you're here, though, you can check out this small demo or [view all demos here](https://github.com/bajuwa/ComicCompiler/blob/master/demos/):   
![ComCom demo](https://github.com/bajuwa/ComicCompiler/blob/master/demos/simple.gif)

## Tutorial 
#### Running ComCom
1. To get started, make sure all your image files are in a single folder on your computer.
      1. For this example, we'll assume your images are all named something like `image001.jpg`.  If this isn't the case, see the [Common Problems](#common-problems) section.
2. Open up that folder in your command line.
3. Run the main `python C:/path/to/comcom.py` command (no additional arguments necessary)
4. At this point, you'll see information printed to your screen.  If all goes well you should see something like `Starting compilation...`.
5. Once the script is done, it will say something like `Compilation Complete` and will stop.  You can then open up the new `./Compiled/` folder in your current directory and see the pages that were generated.
      1. If the pages don't look as you want them, then you'll have to add arguments to adjust the behaviour.  Below in are some common examples, but you can see a complete list in the [Command Line Arguments](https://github.com/bajuwa/ComicCompiler/wiki#command-line-arguments) section.

#### Common Problems       
- Page heights are inconsistent   
       - Try changing the [Breakpoint Mode Detection](https://github.com/bajuwa/ComicCompiler/wiki#breakpoint-detection-mode) via  `-m 1`
- Pages are too short  
       - Increase the [Minimum Height Per Page](https://github.com/bajuwa/ComicCompiler/wiki#minimum-height-per-page) 
- My images aren't named `image001.jpg` / Error: "Cannot find any images"  
       - Change the [Input File Name Prefix](https://github.com/bajuwa/ComicCompiler/wiki#input-file-name-prefix)
       - You can also ignore input file prefix via `-i ""` if you know all the files in the directory are supposed to be included 