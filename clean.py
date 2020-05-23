import glob
import shutil
import os

if __name__ == '__main__':
    for directory in glob.glob("**/*-test/", recursive=True):
        print("deleting: " + directory)
        shutil.rmtree(directory)
    for directory in glob.glob("**/Compiled/", recursive=True):
        print("deleting: " + directory)
        shutil.rmtree(directory)
    if os.path.exists("build/"):
        print("deleting build folder...")
        shutil.rmtree("build/")
    if os.path.exists("dist/"):
        print("deleting dist folder...")
        shutil.rmtree("dist/")
    if os.path.exists("comicom.egg-info/"):
        print("deleting egg-info folder...")
        shutil.rmtree("comicom.egg-info/")
