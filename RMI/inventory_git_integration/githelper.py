import email
import time
import git
from privateData import pwd
import csv
import shutil
import os
import stat
from os import path


local_path = "/Users/heflinjn/Documents/repos/RM-Inventory"
username = "AutoGitBot"
password = pwd.token
target_repo = f"https://{username}:{password}@github.com/JHeflinger/RM-Inventory"

localrepo = git.Repo(local_path)
repoRemote = git.remote.Remote(localrepo, "origin")

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
    with open('RMI/inventory_git_integration/commitLog.csv') as csv_file:
        #read most recent commit stored commit 
        #and clean it to match output format
        csv_reader = list(csv.reader(csv_file, delimiter=','))
        cleanedStr = str(csv_reader[-1])
        cleanedStr = cleanedStr[2:len(cleanedStr)-2]

        #display information about commit history
        print('-----------')
        print(cleanedStr)
        print(recent_datetime)
        print("Last Recorded Change:",cleanedStr)

        #compare most recent commit with stored
        if cleanedStr == str(recent_datetime):
            #write most recent commit to end of 'commitLog.csv' and return false
            with open('RMI/inventory_git_integration/commitLog.csv', mode='a') as commit_log:
                csv_writer = csv.writer(commit_log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([recent_datetime])
            return False

    #write most recent commit to end of 'commitLog.csv' and return true
    with open('RMI/inventory_git_integration/commitLog.csv', mode='a') as commit_log:
        csv_writer = csv.writer(commit_log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([recent_datetime])
    return True

main()