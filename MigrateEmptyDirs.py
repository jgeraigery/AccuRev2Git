#!/usr/bin/env python3

"""
MigrateEmptyDirs.py:
Will traverse local workspace to find empty folders and place a .gitignore file in them.
Python version 3.6
Example args:
    --dirname C:\\repositories\\gitRepo
"""

import os
from subprocess import call
import sys
import time
import getopt

__author__ = "James Newkirk"
__copyright__ = "Copyright 2018, PTC, Inc."

ERR_PARSING_ARGS = 1    # Encounter an error parsing arguments
ERR_UNKNOWN = 2         # Fail unknown reason

def createGitIgnoreFile(gitIgnoreFilePath):
    # Check to see if .gitignore file already exist.
    if not os.path.isfile(gitIgnoreFilePath + '\.gitignore'):
        # Create and open .gitignore file inside of the new directory
        file = open(gitIgnoreFilePath + "\.gitignore", "w+")
        
        # Configure .gitignore file
        file.write("# Ignore everything in this directory\n")
        file.write("*\n")
        file.write("# Except this file\n")
        file.write("!.gitignore")
        
        # Close .gitignore file
        file.close()
        
        print (".gitignore file created at: " + gitIgnoreFilePath + "\.gitignore")
        
    else:
        print(".gitignore file already exists at: " + gitIgnoreFilePath + "\.gitignore")

def findEmptyDirectories(startPath):
    # Crawl through repoPath looking for empty directories. When an empty directory is found, generate a .gitignore
    for (path, dirs, files) in os.walk(startPath, topdown = True, followlinks = False):
        # check if this is an empty directory before removing junctions
        isEmpty = not dirs and not files

        # os.walk follows Windows junctions even when specifying followlinks = False, this will remove them
        with open(os.devnull, 'w') as silent: # ignore the output of fsutil reparsepoint query
            dirs[:] = [d for d in dirs
                       if call(
                           ["fsutil", "reparsepoint", "query", os.path.join(path, d)], 
                           stdout=silent, 
                           stderr=silent
                           ) == 1]

        if isEmpty:
            # Put a .gitignore file inside of the empty directory so that it is no longer empty
            createGitIgnoreFile(path)

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

def main(path):
    try:
        print("Starting MigrateEmptyDirs.py: %s" % time.strftime("%I:%M:%S"))
        findEmptyDirectories(path)
    except Exception as ex:
        print(ex)
        sys.exit(ERR_UNKNOWN)
    finally:
        print("Finished MigrateEmptyDirs.py: %s" % time.strftime("%I:%M:%S"))

if __name__ == '__main__':
    # argument = name of directory to traverse for empty folders
    argument = parse_arguments(sys.argv[1:])
    main(argument)