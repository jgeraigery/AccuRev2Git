#!/usr/bin/env python 3

"""
migrateSingleSnapshot.py:
Creates a single GIT commit based on an Accurev workspace
Example args:
    --accurevStreamName ExampleaccurevStreamName
    --accurevuser name
    --accurevpass pass
    --message "I am a commit message"
"""

import os
import json
import getopt
import sys
import time
import junctions2links
import DownloadAccurevStream
import MigrateEmptyDirs
import workspace2repo
import masterScript
from subprocess import call

__author__ = "Michael C Brown"
__copyright__ = "Copyright 2018, PTC, Inc."

ERR_PARSING_ARGS = 1            # Encounter an error parsing arguments
ERR_UNKNOWN = 2                 # An unknown error as occured

def parse_arguments(argv):
    try:
        print("Importing arguments")
        opts, args = getopt.getopt(argv, "", ["accurevStreamName=",
                                              "accurevuser=",
                                              "accurevpass=",
                                              "message="])
    except Exception as e:
        print(e)
        sys.exit(ERR_PARSING_ARGS)

    for opt, arg in opts:
        if opt == '--accurevStreamName':
            accurevStreamName = arg
        elif opt == '--accurevuser':
            accurevuser = arg
        elif opt == '--accurevpass':
            accurevpass = arg
        elif opt == '--message':
            message = arg

    print("Finished importing arguments")
    return {'accurevStreamName': accurevStreamName, 'username': accurevuser, 'password': accurevpass, 'message': message}

def main(accurevStreamName, username, password, message):
    print("Starting migrateSingleSnapshot.py: %s" % time.strftime("%I:%M:%S"))

    try:
        data = masterScript.parseConfigFile()
        masterScript.startMigrate(username, password, data['gitRepo'], accurevStreamName, None, data['blacklist'], message)
        masterScript.ignoreBinaries(data['gitRepo'])

    except Exception as e:
        print(e)
        sys.exit(ERR_UNKNOWN)
    finally:
        print("Finishing migrateSingleSnapshot.py: %s" % time.strftime("%I:%M:%S"))


if __name__ == '__main__':
    arguments = parse_arguments(sys.argv[1:])
    main(arguments['accurevStreamName'], arguments['username'], arguments['password'], arguments['message'])
