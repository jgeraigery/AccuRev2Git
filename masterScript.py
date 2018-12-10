#!/usr/bin/env python3

"""
masterScript.py:
Automate migration from AccuRev to local git repo using the Tyler structure.
Python version 3.6
Example args:
    --accurevuser name
    --accurevpass pass
"""

import getopt
import os
import sys
import time
from datetime import datetime
from shutil import copy
from subprocess import call
import json
import junctions2links
import DownloadAccurevStream
import MigrateEmptyDirs
import workspace2repo

__author__ = "Kiersten Marr"
__copyright__ = "Copyright 2018, PTC, Inc."

ERR_PARSING_ARGS = 1    # Encounter an error parsing arguments
ERR_UNKNOWN = 2         # Fail unknown reason
ERR_GIT = 3             # Failure calling git command
ERR_JSON = 4            # Failure loading json file

def CopyGitIgnore(localdir):
    copy(os.path.join(os.getcwd(), "gitignoreForMigration"), os.path.join(localdir, ".gitignore"))

def startMigrate(accurevuser, accurevpass, localdir, streamname, tag, blacklist, message = None):
    # delete everything in local git repo except .git
    if os.path.exists(localdir):
        gitCallHandler(["rm", "-rf", "."], localdir)
    else:
        print("localdir not created yet. Continuing . . . ")

    transaction = DownloadAccurevStream.main(streamname, localdir, accurevuser, accurevpass, blacklist)

    # Append transaction number which was migrated
    if message != None:
        message += '\n\nTransaction Number: ' + transaction

    CopyGitIgnore(localdir)
    junctions2links.main(localdir)
    MigrateEmptyDirs.main(localdir)
    workspace2repo.main(localdir, tag, message)

def ignoreBinaries(localdir):
    with open(os.path.join(localdir, '.gitignore'), 'a+') as gitignoreFile:
        gitignoreFile.write('\n'.join(["\n", "# Java build output", ".gradle/", ".idea/"]))
        gitignoreFile.write('\n'.join(["\n", "# Binary extensions", "*.bin", "*.bmp", "*.cfx", "*.dat", "*.der",
                                       "*.dll", "*.docx", "*.exe", "*.gif", "*.ico", "*.jpg", "*.lib", "*.mdb",
                                       "*.msi", "*.opf", "*.png", "*.pdf", "*.pptx", "*.xlsx", "*.zip"]))
    
    # add and commit the update gitignore file
    gitCallHandler(["add", localdir], localdir)
    gitCallHandler(["commit", "-m", 'Ignore future binary files', '--author="GeneralUser <GeneralUser@ptc.com>"'], localdir)

def gitCallHandler(cmd, localdir):
    try:
        returnCode = call(["git", "-C", localdir] + cmd)
        if returnCode == 0:
            print("Successfully executed command: git " + " ".join(cmd))
        else:
            print("Failed to execute command: git " + " ".join(cmd))
            sys.exit(ERR_GIT)
    except Exception as e:
        print(e)
        sys.exit(ERR_UNKNOWN)

def parse_arguments(argv):
    try:
        print("Importing arguments")
        opts, args = getopt.getopt(argv, "", ["accurevuser=",
                                              "accurevpass="])
    except Exception as e:
        print(e)
        sys.exit(ERR_PARSING_ARGS)

    for opt, arg in opts:
        if opt == '--accurevuser':
            accurevuser = arg
        elif opt == '--accurevpass':
            accurevpass = arg
    try: 
        print("Finished importing arguments")
        return {'username': accurevuser, 'password': accurevpass}
    except UnboundLocalError as e:
        print("Could not find necessary arguments. Exiting . . . ")
        print(e)
        sys.exit(ERR_UNKNOWN)

def parseConfigFile():
    with open(os.path.join(os.getcwd(), 'config.json')) as configFile:
            try:
                return json.load(configFile)
            except ValueError:
                print("Error loading JSON.")
                sys.exit(ERR_JSON)

def main(accurevuser, accurevpass):
    try:
        print("Starting masterScript.py: %s" % time.strftime("%I:%M:%S"))
        startTime = datetime.now()
        data = parseConfigFile()

        localdir = data['gitRepo']
        blacklist = data['blacklist']

        for release in data['releases']:
            version = release['Version']
            releaseStream = release['StreamName']
            relTag = release['ReleaseTag']
            startMigrate(accurevuser, accurevpass, localdir, releaseStream, relTag, blacklist)

            # create maintenance branch and fill it
            branchName = version + "_Maint"

            # Note: gitCallHandler will catch a fatal error if this branch already exists.
            #       This should not happen since this script first creates our current repo.
            gitCallHandler(["checkout", "-b", branchName], localdir)

            for stream in release['Maint']:
                maint = stream['name']
                tag = stream['tag']
                startMigrate(accurevuser, accurevpass, localdir, maint, tag, blacklist)

            # prevent new binaries from being added to this maintenance branch in future commits
            ignoreBinaries(localdir);

            # return to master
            gitCallHandler(["checkout", "master"], localdir)

        # prevent new binaries from being added to the master branch in future commits
        # this will also block all binaries on any branch created off of master from this point forward
        ignoreBinaries(localdir);
        
    except Exception as ex:
        print(ex)
        sys.exit(ERR_UNKNOWN)
    finally:
        print("Finished masterScript.py: %s" % time.strftime("%I:%M:%S"))
        print("Operations took %s" % (datetime.now() - startTime))
    sys.exit(0)

if __name__ == '__main__':
    arguments = parse_arguments(sys.argv[1:])
    main(arguments['username'], arguments['password'])