import email
import time
import git
import csv
import shutil
import os
import stat
from os import path
from pathlib import Path
from os.path import exists

password = ""
if exists("tokens/authtoken.tkn"):
    with open("tokens/authtoken.tkn", "r") as t:
        password = t.readline()
else:
    print("Error: Admin token not found. Please request an authentication token from an admin.")
    exit()
full_path = Path.cwd().__str__();
local_path = full_path[0:len(full_path) - 4];
username = "AutoGitBot"
target_repo = f"https://{username}:{password}@github.com/JHeflinger/RM-Inventory"
localrepo = git.Repo(local_path)
repoRemote = git.remote.Remote(localrepo, "origin")

#machines will need to either run this command or store their credentials in .git/config
#git.Repo.clone_from(target_repo, local_path)

def main():
    #used for displaying approx. runtime and 
    #show when most recent commit was accepted 
    total_times_checked = 0
    time_since_last_pull = 0

    while True:
        #Update Counters
        total_times_checked += 1
        time_since_last_pull +=1
        
        #Pull all commits, check/store most recent in 'recent_Commit'
        print('[',time_since_last_pull, '||' ,total_times_checked,']Now Checking for new Commits...')
        commits = list(localrepo.iter_commits())
        recent_Commit=commits[0].committed_datetime


        #True when new files written to github
        if compare(recent_Commit):
            #update counter
            time_since_last_pull = 0

            #pull the repo 
            repoRemote.pull()
            print("Pulled")

        #Pull every (x) seconds
        time.sleep(10)

def compare(recent_datetime):
    with open('commitLog.csv') as csv_file:
        #read most recent commit stored commit 
        #and clean it to match output format
        csv_reader = list(csv.reader(csv_file, delimiter=','))
        cleanedStr = str(csv_reader[-1])
        cleanedStr = cleanedStr[2:len(cleanedStr)-2]

        #compare most recent commit with stored
        if cleanedStr == str(recent_datetime):
            #write most recent commit to end of 'commitLog.csv' and return false
            with open('commitLog.csv', mode='a') as commit_log:
                csv_writer = csv.writer(commit_log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([recent_datetime])
            return False

    #write most recent commit to end of 'commitLog.csv' and return true
    with open('commitLog.csv', mode='a') as commit_log:
        csv_writer = csv.writer(commit_log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([recent_datetime])
    return True

def gitPull():
    commits = list(localrepo.iter_commits())
    recent_Commit=commits[0].committed_datetime
    if compare(recent_Commit):
        repoRemote.pull()

def gitCommit(filepath, commitMessage):
    try:
        localrepo.git.add(filepath)
        localrepo.index.commit(commitMessage)
        return True
    except:
        return False

def gitPush():
    try:
        origin = localrepo.remote(name="origin")
        origin.push()
        return True
    except:
        return False