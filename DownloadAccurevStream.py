#!/usr/bin/env python3

"""
DownloadAccurevStream.py:
Download AccuRev stream to local directory
Example args:
    --streamname PROJECT_1.0.101.0_REL
    --dirname C:\\repositories\\gitRepo
    --accurevuser name
    --accurevpass pass
"""

import getopt
import os
import shutil
import sys
import time
from subprocess import call

__author__ = "Samuel M Gile"
__copyright__ = "Copyright 2018, PTC, Inc."

ERR_PARSING_ARGS = 1    # Encounter an error parsing arguments
ERR_UNKNOWN = 2         # Fail unknown reason
ERR_ACCUREV = 3         # Error communicating with Accurev
ERR_CREATEDIR = 4       # Creating directory
ERR_DELETION = 5        # Error deleting blacklisted path

class Accurev:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.transaction = ""

    def login(self):
        try:
            print("Logging into AccuRev as user: %s" % self.username)
            returnCode = call(["accurev", "login", "-H", "URLtoAccuRevServer:Port", self.username, self.password])
            if returnCode == 0:
                print("Successful login to Accurev")
            else:
                print("Failed login to Accurev!")
                sys.exit(ERR_ACCUREV)
        except Exception as ex:
            print(ex)
            sys.exit(ERR_ACCUREV)

    def download(self, stream_name, dirname):
        create_directory(dirname)

        try:
            print("Downloading stream %s files to directory %s" % (stream_name, dirname))
            self._getTransactionNumber(stream_name)
            with open(os.devnull, 'w') as silent:
                returnCode = call(["accurev", "pop", "-R", "-v" + stream_name, "-L" + dirname, "-t" + self.transaction,
                                   ".\\"], stdout=silent)
            if returnCode == 0:
                print("Successfully downloaded stream %s from AccuRev" % stream_name)
                print("Local download directory: %s" % dirname)
            else:
                print("Failed to download files from AccuRev!")
                sys.exit(ERR_ACCUREV)
        except Exception as ex:
            print(ex)
            sys.exit(ERR_ACCUREV)

    def _getTransactionNumber(self, stream_name):
        # if filestream.txt already exists
        try:
            os.remove('filestream.txt')
        except OSError:
            pass
        # ran into issues with String.IO, had to use text file
        with open('filestream.txt', 'w+') as filestream:
            try:
                call(["accurev", "hist", "-ft", "-s" + stream_name, "-t", "now.1"], stdout=filestream)
            except Exception as ex:
                print(ex)
                sys.exit(ERR_ACCUREV)
        with open('filestream.txt', 'r') as file:
            # Find the desired line, seems to always be a blank line preceding the desired line
            for line in file.readlines():
                if line.split(" ")[0] == "transaction":
                    break
            self.transaction = line.split(";")[0].split(" ")[1]

def create_directory(dir):
    try:
        if os.path.exists(dir):
            print ("Local directory already exists")
        else:
            os.mkdir(dir)
            print ("Successfully created the directory %s " % dir)
            try:
                returncode = call(["git", "init", dir])
                if returncode == 0:
                    print("Successfully initialized git repo.")
                else:
                    print("Failed to execute git repo initialization.")
                    sys.exit(ERR_UNKNOWN)
            except Exception as e:
                print(e)
                sys.exit(ERR_UNKNOWN)
    except OSError as ex:  
        print ("Creation of the directory %s failed\n%s" % (dir, ex))
        sys.exit(ERR_CREATEDIR)

def deletePaths(dirname, blacklist):
    for item in blacklist:
        filepath = dirname + item
        try:
            if os.path.exists(filepath):
                try:
                    call("rmdir /s /q " + '"' + filepath + '"', shell=True)
                    print("Successfully removed " + filepath)
                except Exception as ex:
                    print("os.system calling of command did not work due to: " + ex)
                    sys.exit(ERR_DELETION)
            else:
                print("Path %s does not exist." % filepath)
        except Exception as e:
            print ("Deletion of path %s failed\n%s" % (filepath, e))
            sys.exit(ERR_DELETION)

def parse_arguments(argv):
    try:
        print("Importing arguments")
        opts, args = getopt.getopt(argv, "", ["streamname=",
                                              "dirname=",
                                              "accurevuser=",
                                              "accurevpass=",
                                              "blacklist="])
    except Exception as e:
        print(e)
        sys.exit(ERR_PARSING_ARGS)

    for opt, arg in opts:
        if opt == '--streamname':
            streamname = arg
        elif opt == '--dirname':
            dirname = arg
        elif opt == '--accurevuser':
            accurevuser = arg
        elif opt == '--accurevpass':
            accurevpass = arg
        elif opt == '--blacklist':
            blacklist = arg

    print("Finished importing arguments")
    return {'streamname': streamname, 'dirname': dirname, 'user': accurevuser, 'pass': accurevpass, 'blacklist': blacklist}  

def main(streamname, dirname, accurevuser, accurevpass, blacklist):
    try:
        print("Starting DownloadAccurevStream.py: %s" % time.strftime("%I:%M:%S"))
        accurev = Accurev(accurevuser, accurevpass)
        accurev.login()
        accurev.download(streamname, dirname)
        deletePaths(dirname, blacklist)
    except Exception as ex:
        print(ex)
        sys.exit(ERR_UNKNOWN)
    finally:
        try:
            os.remove('filestream.txt')
        except OSError:
            pass
        print("Finished DownloadAccurevStream.py: %s" % time.strftime("%I:%M:%S"))
        return accurev.transaction


if __name__ == '__main__':
    args = parse_arguments(sys.argv[1:])
    main(args['streamname'], args['dirname'], args['user'], args['pass'], args['blacklist'])