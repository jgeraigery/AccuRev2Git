
## Overview

The automated migration includes 1 master script, 4 subscripts, and 1 JSON configuration file. By running the master script with a correctly configured JSON, you can migrate AccuRev streams and their maintenance streams over to a local Git repo in the historical branching structure. All scripts but the master script can be run alone. Argument structure is provided below if you prefer to run a subscript alone.

The historical branching structure is a branching scheme in which releases are tagged and stacked sequentially on the master branch. Each release has a maintenance branch stemming from it, containing any associated maintenance streams from AccuRev.


## Licensing
Please see the file called LICENSE.md

## The following scripts are used for migration

### DownloadAccurevStream.py

Populates a local workspace with the specified stream from AccuRev. Deletes unnecessary folders and files from the local workspace based on a blacklist provided by config.json. Initializes a Git repository in the workspace to later commit the desired files and folders to. Note that if running this script individually, a .git file will still be created in the local workspace.

- Arguments
    > **--streamname** exampleStream **--dirname** exampleDirectory **--accurevuser** exampleUser **--accurevpass** examplePass

### MigrateEmptyDirs.py

Traverses through the local workspace taken from AccuRev, finds all empty folders, and places a .gitignore file in them. This prevents the folders from being deleted when they are added and committed to Git.

- Arguments     
    > **--dirname** exampleDirectory

### junctions2links.py

Finds all windows junctions in a local workspace and converts them to symbolic links. Git does not support junctions but does support symbolic links.

- Arguments
    > **--dirname** exampleDirectory

### workspace2repo.py

Turns workspace into local repository. Adds, commits, and tags the current stream in the workspace. Stream will then be present in the local Git repo.

- Arguments
    > **--dirname** exampleDirectory **--tag** exampleTag

### masterScript.py

The master script to call all subscripts, input json parameters, and implement the historical branching structure.

- Arguments
    > **--accurevuser** exampleUser **--accurevpass** examplePass

### migrateSingleSnapshot.py

Creates a single commit based on an AccuRev workspace in an existing git repository. The desired branch should be checked out prior to running this script.

- Arguments
    > **--accurevStreamName** ExampleaccurevStreamName **--accurevuser** exampleUser **--accurevpass** examplePass **--message** "I am a commit message"

### moveFiles.py

Diff two AccuRev streams/snapshots and see which files were moved. Then move the same files in a git repo. The desired branch should be checked out prior to running this script.

- Arguments

    > **--accurevStreamName1** ExampleaccurevStreamName1 **--accurevStreamName2** ExampleaccurevStreamName2 **--accurevuser** exampleUser **--accurevpass** examplePass **--message** "Moving Files"

### config.json

Configuration file to specify inputs to master script. Includes:
- **gitRepo**: the name of the path (which cannot previously exist) which you want to put the AccuRev stream into and convert into a Git repo.
- **blacklist**: an array of all folders and files you want to remove before committing to Git.
- **releases**: an array in which you include all release streams, their  **Version**, their  **ReleaseTag**, and an array of associated maintenance streams for each release.


## Using masterScript.py and subscripts

1.  Alter config.json. Fill blacklist array with the names of folders that you do not want in Git. Enter version name and desired tag name. Put names and tags of maintenance streams in Maint array. If no maintenance streams, leave the array empty. Change gitRepo to a local path where you would like to put the local Git repo. The path must not already exist. If it does, it will be deleted. The provided JSON file is currently filled with example streams.
1.  Run the master script using two arguments: AccuRev username and AccuRev password. If running from Visual Studio, check that the correct script arguments are set. If from the command line, run as follows (substituting your own username and password):
    
    ```
    python masterScript.py --accurevuser name --accurevpass pass
    ```

1.  Master script should take some time to run due to pulling streams down from AccuRev. Recommended that this be run overnight or over a weekend.
1.  This script will only take streams from a remote AccuRev repository to make a local Git repository. The final step is to push the local Git repository to the remote GitLab instance. To do this you use the command  **git push --mirror git@sample:root/prod.git**, which will push everything locally to the remote repository including all tags.


## Using migrateSingleSnapshot.py:

1.  Alter config.json. Fill blacklist array with the names of folders that you do not want in Git. Change gitRepo to the local path where the existing git repo is located. The releases section is ignored for this file.
1.  Run the script using four arguments: AccuRev stream name, AccuRev username, AccuRev password, and the commit message. If running from Visual Studio, check that the correct script arguments are set. If from the command line, run as follows (substituting your own argument values):

    ```
    python migrateSingleSnapshot.py --accurevStreamName ExampleaccurevStreamName --accurevuser exampleUser --accurevpass examplePass --message "I am a commit message"
    ```

1.  The script should take around half an hour to run due to pulling the stream down from AccuRev.
1.  This script will only take streams from a remote AccuRev repository to make a local Git repository. The final step is to push the local Git repository to the remote GitLab instance. To do this you use the command git push --mirror git@sample:root/prod.git, which will push everything locally to the remote repository including all tags.


## Using moveFiles.py:

1.  Alter config.json. Change gitRepo to the local path where the existing git repo is located. The blacklist and releases sections are ignored for this file.
1.  Run the script using five arguments: First AccuRev stream name, Second AccuRev stream name, AccuRev username, AccuRev password, and the commit message. If running from Visual Studio, check that the correct script arguments are set. If from the command line, run as follows (substituting your own argument values):

    ```
    python migrateSingleSnapshot.py --accurevStreamName1 ExampleaccurevStreamName1 --accurevStreamName2 ExampleaccurevStreamName2 --accurevuser exampleUser --accurevpass examplePass --message "I am a commit message"
    ```

1.  The script will find which files have been moved between ExampleaccurevStreamName1 and ExampleaccurevStreamName2. These files will then be moved in git just as they were in AccuRev with no other changes applied and a commit made for this move.
1.  This script will only take streams from a remote AccuRev repository to make a local Git repository. The final step is to push the local Git repository to the remote GitLab instance. To do this you use the command git push --mirror git@sample:root/prod.git, which will push everything locally to the remote repository including all tags.
Usually migrateSingleSnapshot.py should then be run after this script to also perform any necessary changes to the files.


## Notes

- Subscripts and master script run on python 3.6
- config.json and scripts must be in the same location locally.
- Adding "> output.txt" to the command line arguments of masterScript.py will redirect the output to a file for viewing later
- The results can be verified using Visual Studio, Sourcetree, or through the command line before pushing to GitLab:
    
    ```
    git log
    git show-branch -a
    git log --all --decorate --online --graph
    ```