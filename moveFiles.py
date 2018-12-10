#!/usr/bin/env python 3

"""
moveFiles.py:
Diff two AccuRev streams/snapshots and see which files were moved. Then move the same files in a git repo.
Example args:
    --accurevStreamName1 ExampleaccurevStreamName1
    --accurevStreamName2 ExampleaccurevStreamName2
    --accurevuser name
    --accurevpass pass
    --message "Moving Files"
"""

import os
import getopt
import sys
import time
import DownloadAccurevStream
import masterScript
from subprocess import call

__author__ = "Corey Birdsall"
__copyright__ = "Copyright 2018, PTC, Inc."

ERR_PARSING_ARGS = 1            # Encounter an error parsing arguments
ERR_UNKNOWN = 2                 # An unknown error as occured

def parse_arguments(argv):
    try:
        print("Importing arguments")
        opts, args = getopt.getopt(argv, "", ["accurevStreamName1=",
                                              "accurevStreamName2=",
                                              "accurevuser=",
                                              "accurevpass=",
                                              "message="])
    except Exception as e:
        print(e)
        sys.exit(ERR_PARSING_ARGS)

    for opt, arg in opts:
        if opt == '--accurevStreamName1':
            accurevStreamName1 = arg
        elif opt == '--accurevStreamName2':
            accurevStreamName2 = arg
        elif opt == '--accurevuser':
            accurevuser = arg
        elif opt == '--accurevpass':
            accurevpass = arg
        elif opt == '--message':
            message = arg

    print("Finished importing arguments")
    return {'accurevStreamName1': accurevStreamName1, 'accurevStreamName2': accurevStreamName2, 'username': accurevuser, 'password': accurevpass, 'message': message}

def getFilesToMove():
    filesToMove = []
    with open('filestream.txt', 'r') as file:
        for line in file.readlines():
            searchString = "moved to"
            if searchString in line:
                searchStringPlace = line.find(searchString)
                searchStringLength = len(searchString)
                source = line[:searchStringPlace].strip()
                target = line[searchStringPlace + searchStringLength:].strip()
                filesToMove.append([source.strip("/./"),target.strip("/./")])
    return filesToMove

def moveFiles(filesToMove, message, gitRepo):
    for source, target in filesToMove:
        # Verify that target is not a directory
        # Renamed directories don't work with git mv and will be handled as part of moving the files inside
        if "." not in os.path.basename(target):
            continue
        # Create the directories if needed
        targetDirectory = os.path.join(gitRepo, os.path.dirname(target))
        if not os.path.exists(targetDirectory):
            os.makedirs(targetDirectory)
        masterScript.gitCallHandler(["mv", "-v", source, target], gitRepo)
    masterScript.gitCallHandler(["commit", "-m", message, '--author="GeneralUser <GeneralUser@ptc.com>"'], gitRepo)

def main(accurevStreamName1, accurevStreamName2, username, password, message):
    print("Starting moveFiles.py: %s" % time.strftime("%I:%M:%S"))

    try:
        data = masterScript.parseConfigFile()

        accurev = DownloadAccurevStream.Accurev(username, password)
        accurev.login()

        # if filestream.txt already exists
        try:
            os.remove('filestream.txt')
        except OSError:
            pass

        # ran into issues with String.IO, had to use text file
        with open('filestream.txt', 'w+') as filestream:
            # diff returns 0 for no differences, 1 for differences, 2 for error
            returnCode = call(["accurev", "diff", "-v", accurevStreamName1, "-V", accurevStreamName2, "-a", "-i"], stdout=filestream)
            if returnCode == 0:
                return
            elif returnCode == 1:
                filesToMove = getFilesToMove()
                moveFiles(filesToMove, message, data['gitRepo'])
            else:
                print("Failed diff streams in Accurev!")
                sys.exit(DownloadAccurevStream.ERR_ACCUREV)
        
    except Exception as e:
        print(e)
        sys.exit(ERR_UNKNOWN)
    finally:
        try:
            os.remove('filestream.txt')
        except OSError:
            pass
        print("Finishing moveFiles.py: %s" % time.strftime("%I:%M:%S"))


if __name__ == '__main__':
    arguments = parse_arguments(sys.argv[1:])
    main(arguments['accurevStreamName1'], arguments['accurevStreamName2'], arguments['username'], arguments['password'], arguments['message'])
