#!/usr/bin/python

# import subprocess
import argparse

# Initiate the parser
programDescription = "Given a set of images, vertically combines them in to 'pages' where the start/end of the page " \
                     "are solid white (or some other specified colour)."
parser = argparse.ArgumentParser(description=programDescription)

parser.add_argument("-m", "--min-height-per-page", default=5000, type=int,
                    help="The minimum allowed pixel height for each output page")
# parser.add_argument("-M", "--max-height-per-page", default=15000, type=int,
#                     help="The maximum allowed pixel height for each output page")
parser.add_argument("-i", "--input-file-prefix", default="image", type=str,
                    help="Will only combine images that start with this text")
parser.add_argument("-e", "--extension", default=".jpg", type=str,
                    help="The file extension of your input images and your output page files.")
parser.add_argument("-o", "--output-file-prefix", default="page", type=str,
                    help="The text that will go at the start of each output page name prior to the 3 digit zero "
                         "padded page number.")
parser.add_argument("-osn", "--output-file-starting-number", default=1, type=int,
                    help="The number of the first output page.")
parser.add_argument("-ow", "--output-file-width", default=0, type=int,
                    help="The explicit width of the output pages. If no value is given, or a value of 0 is given, "
                         "then the output pages will be the same width as the first input image.")
parser.add_argument("-id", "--input-directory", default="./", type=str,
                    help="The path to the directory you want to collect image files from.")
parser.add_argument("-is", "--include-sub-directories",
                    help="This will include images in subdirectories.")
parser.add_argument("-od", "--output-directory", default="./Compiled/", type=str,
                    help="The path to the directory you want to put the new page files in.")
parser.add_argument("-b", "--breakpoint-detection-mode", default=0, type=int,
                    help="The 'mode' that the script uses to detect where to split up pages. Mode 0 will split pages "
                         "when an input image ends in a breakpoint colour. Mode 1 will scan throughtout the input "
                         "images to find a breakpoint.")
parser.add_argument("-bi", "--break-points-increment", default=10, type=int,
                    help="When in Breakpoint Detection Mode #1 this value controls how often the script tests a line "
                         "in an image file for a breakpoint.")
parser.add_argument("-bm", "--break-points-multiplier", default=20, type=int,
                    help="When in Breakpoint Detection Mode #1 this value controls how large of a vertical area is "
                         "pre-tested for a breakpoint before iterating over rows via Breakpoint Row Check Increments.")
parser.add_argument("-c", "--split-on-colour", default=[0, 65355], type=int, nargs="+",
                    help="The list of decimal notation colours you want to split on. Use 65535 for white, 0 for black, "
                         "or any number in that range for your intended colour.")
parser.add_argument("-C", "--additional-split-on-colour", default=[], type=int, nargs="+",
                    help="The list of decimal notation colours you want to split on in addition to the provided "
                         "defaults in SPLIT_ON_COLOUR.")
parser.add_argument("-ce", "--colour-error-tolerance", default=0, type=int,
                    help="The error tolerance used when testing whether a specific image/row matches the given "
                         "breakpoint colour")
parser.add_argument("--exit", action="store_true",
                    help="If set, when the program finishes compiling it will prompt you to press enter before "
                         "terminating itself.")
parser.add_argument("--clean", action="store_true",
                    help="If set, before the new pages are compiled the program will delete the configured output "
                         "directory.")
parser.add_argument("--open", action="store_true",
                    help="If set, after the new pages are compiled the program will open the directory it was working "
                         "in via windows explorer.")

parser.add_argument("-l", "--logging-level", default=0, type=int,
                    help="Sets logging level [0 for basic, 1 for debug, 2 for verbose]")
parser.add_argument("--debug", action="store_true", help="Turns on debug level logging")
parser.add_argument("--verbose", action="store_true", help="Turns on verbose level logging")

args = parser.parse_args()

args.split_on_colour += args.additional_split_on_colour
if args.debug:
    args.logging_level = 1
if args.verbose:
    args.logging_level = 2

if (args.logging_level > 0):
    print("Running with args: %s" % args)


# Verify that imagemagick is installed/accessible

# Possible to do the 'erase line and reprint' logging?

# Need to redesign how the data should be gathered/passed around (global vars are bad)

# Object for 'Page' that contains:
#   - ordered image file names to combine
#   - cumulativePageHeight
#   - crop values

# Simple functions to make first + test
#   findInputImages
#   ensureDirectory
#   ensureConsistentWidth

# Complex functions to port
#   fileEndsInBreakPoint
#   findBreakPoint
#   fileSampleContainsColour
#   cropFromTopAndBottom
#   findBatchSizeForNextPage
#   combineImages


# Main program (ie this file) should only contain the following logic, all other methods should be contained elsewhere

# if [[ ${#imageFileNames[@]} -eq 0 ]];
# then
# echo "Couldn't find any images to combine";
# else
# echo "Starting compilation..."
# start=$(date +%s)
# ensureDirectory ${OUTPUT_DIRECTORY};
# ensureConsistentWidth ${OUTPUT_PAGE_WIDTH};
# combineImages;
# end=$(date +%s)
# totalTime=$(($end-$start))
# echo "Comic Compilation - Complete! (time: "${totalTime}"s)"
# fi
#
# if [[ ${OPEN_ON_COMPLETE} -eq 0 ]]
# then
# explorer . &
# fi
#
# if [[ ${CONFIRM_EXIT} -eq 0 ]]
# then
# echo ""
# read -p "Press enter to exit"
# fi