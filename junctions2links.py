#!/usr/bin/env python3

"""
junctions2links.py:
Convert junctions into symlinks.
Python version 3.6
Example args:
    --dirname C:\\repositories\\gitRepo
"""

import os
from subprocess import call
import sys
import time
import getopt

__author__ = "Kiersten Marr"
__copyright__ = "Copyright 2018, PTC, Inc."

ERR_PARSING_ARGS = 1    # Encounter an error parsing arguments
ERR_UNKNOWN = 2         # Fail unknown reason

def findJunctions(rpath):
    for (path, dirs, files) in os.walk(rpath, topdown = True, followlinks = False):
        nonJunctionDirs=[]
        for d in dirs:
            # if filestream.txt already exists
            try:
                os.remove('filestream.txt')
            except OSError:
                pass
            # ran into issues with String.IO, had to use text file
            with open('filestream.txt', 'w+') as filestream:
                with open(os.devnull, 'w') as silent:
                    fullpath = os.path.join(path, d)
                    if call(["fsutil", "reparsepoint", "query", fullpath], stdout=filestream, stderr=silent) == 0:
                        target = str(getTarget(fullpath))
                        # if already symbolic link, target may return None
                        if target != "None":
                            symlinkCreate(fullpath, target, path)
                    else:
                        nonJunctionDirs.append(d)
                # Erase previous file contents so that new output of fsutil reparsepoint can
                # write in new output for next path checked.
                filestream.seek(0)
                filestream.truncate()

        dirs[:] = nonJunctionDirs

def getTarget(path):
    with open('filestream.txt', 'r') as file:
        for line in file.readlines():
            searchString = "\\??\\"
            if "Substitute" in line and searchString in line:
                stringPlace = line.find(searchString)
                start = stringPlace + len(searchString)
                target = line[start:].strip()
                return target

def symlinkCreate(fullpath, target, path):
    with open(os.devnull, 'w') as silent:
        # delete junction w/o removing destination
        call(["fsutil", "reparsepoint", "delete", fullpath], stdout=silent, stderr=silent)
        os.rmdir(fullpath)

        relativePath = os.path.relpath(target, path)

        call(["mklink", "/d", fullpath, relativePath], stdout=silent, stderr=silent, shell=True)
        print("Success: A link was created from " + fullpath + " to " + target)

def parse_arguments(argv):
    try:
        print("Importing arguments")
        opts, args = getopt.getopt(argv, "", ["dirname="])

    except Exception as e:
        print(e)
        sys.exit(ERR_PARSING_ARGS)

    for opt, arg in opts:
        if opt == '--dirname':
            dirname = arg

    print("Finished importing arguments")
    return dirname

def main(rpath):
    try:
        print("Starting junctions2links.py: %s" % time.strftime("%I:%M:%S"))
        findJunctions(rpath)
    except Exception as ex:
        print(ex)
        sys.exit(ERR_UNKNOWN)
    finally:
        try:
            os.remove('filestream.txt')
        except OSError:
            pass
        print("Finished junctions2links.py: %s" % time.strftime("%I:%M:%S"))


if __name__ == '__main__':
    # argument = name of directory to traverse for junctions
    argument = parse_arguments(sys.argv[1:])
    main(argument)