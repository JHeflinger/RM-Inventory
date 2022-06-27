import email
import time
import git
from privateData import pwd
import csv
import shutil
import os
import stat
from os import path



#Used for commit checking
#/mcdanibj/Desktop -> /mcdanbj2
local_path = "/home/mcdanbj2/dispenser"
username = "Ben-McDaniel"
password = pwd.token
target_repo = f"https://{username}:{password}@github.com/Ben-McDaniel/dispenser"



#Used for pulling from repo
#/mcdanibj/Desktop -> /mcdanbj2
localrepo = git.Repo("/home/mcdanbj2/dispenser")
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



#returns true when the most recent commit to the 
#github does not match the last recorded in 'commitLog.csv'
def compare(recent_datetime):
    with open('commitLog.csv') as csv_file:
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
            with open('commitLog.csv', mode='a') as commit_log:
                csv_writer = csv.writer(commit_log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csv_writer.writerow([recent_datetime])
            return False

    #write most recent commit to end of 'commitLog.csv' and return true
    with open('commitLog.csv', mode='a') as commit_log:
        csv_writer = csv.writer(commit_log, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([recent_datetime])
    return True



#<--------------DEPRICATED-------------->
#deletes repo, must do this way to allow deleting
#read-only .git files
def deleteRepo(local_path):
    for root, dirs, files in os.walk(local_path):  
        for dir in dirs:
            os.chmod(path.join(root, dir), stat.S_IRWXU)
        for file in files:
            os.chmod(path.join(root, file), stat.S_IRWXU)
    shutil.rmtree(local_path)



if __name__ == "__main__":
    main()