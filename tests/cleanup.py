import glob
import shutil

if __name__ == '__main__':
    for directory in glob.glob("**/tests/**/*-test/", recursive=True):
        shutil.rmtree(directory)
