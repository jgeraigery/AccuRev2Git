#!/usr/bin/env python 3

"""
workspace2repo.py:
Setup an AccuRev workspace to become a git repository. Adds, commits, and tags repository.
Example args:
    --dirname C:\\repositories\\gitRepo
    --tag ExampleTag
"""

import os
import getopt
import sys
import time
from subprocess import call

__author__ = "James Newkirk"
__copyright__ = "Copyright 2018, PTC, Inc."

ERR_PARSING_ARGS = 1          # Encounter an error parsing arguments
ERR_SETTING_WORKING_DIR = 2   # Encounter an error setting the working directory
ERR_GIT = 3                   # Encounter an error calling a git command
ERR_UNKNOWN = 4               # An unknown error as occured

def parse_arguments(argv):
    try:
        print("Importing arguments")
        opts, args = getopt.getopt(argv, "", ["dirname=",
                                              "tag=",])
    except Exception as e:
        print(e)
        sys.exit(ERR_PARSING_ARGS)

    for opt, arg in opts:
        if opt == '--dirname':
            dirname = arg
        elif opt == '--tag':
            tag = arg

    print("Finished importing arguments")
    return {'dirname': dirname, 'tag': tag}

def gitCaller(cmd, dirname):
    try:
        returnCode = call(["git", "-C", dirname] + cmd)
        if returnCode == 0:
            print("Successfully executed command: git " + " ".join(cmd))
        else:
            print("Failed to execute command: git " + " ".join(cmd))
            sys.exit(ERR_GIT)
    except Exception as e:
        print(e)
        sys.exit(ERR_UNKNOWN)

# Take in path to workspace. Add and commit to git
def commitRepo(dirname, tag, message=""):
    gitAdd = ["add", dirname]
    gitCaller(gitAdd, dirname)
    if tag == "":
        gitCommit = ["commit", "--allow-empty", "-m", 'Added Maint', '--author="GeneralUser <GeneralUser@ptc.com>"']
    elif tag == None:
        gitCommit = ["commit", "--allow-empty", "-m", message, '--author="GeneralUser <GeneralUser@ptc.com>"']
    else:
        gitCommit = ["commit", "--allow-empty", "-m", 'Added ' + tag, '--author="GeneralUser <GeneralUser@ptc.com>"']
    gitCaller(gitCommit, dirname)

# Add specified tag to repo
def addTag(tag, dirname):
    if tag not in ["", None]:
        gitTag = ["tag", tag]
        gitCaller(gitTag, dirname)

# Take in path to workspace. Initialize, add, and commit to git. Add specified tag to repo
def main(dirname, tag, message):
    print("Starting workspace2repo.py: %s" % time.strftime("%I:%M:%S"))

    try:
        commitRepo(dirname, tag, message)
        addTag(tag, dirname)
    except Exception as e:
        print(e)
        sys.exit(ERR_UNKNOWN)
    finally:
        print("Finishing workspace2repo.py: %s" % time.strftime("%I:%M:%S"))


if __name__ == '__main__':
    arguments = parse_arguments(sys.argv[1:])
    main(arguments['dirname'], arguments['tag'])