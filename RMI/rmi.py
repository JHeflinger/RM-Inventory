import csv
from csv import writer
import hashlib
import githelper
from datetime import datetime

#variables
global universalCommands
global defaultCommands
global userCommands
global adminCommands
global userStatus
global username
global password
global offline
global fakeDatabase
global activityMessage
global validTypes
offline = False
activityMessage = ""
fakeDatabase = []
userStatus = "default" #can be default, user, or admin
username = ""
password = ""
universalCommands = "\thelp - brings up a list of available commands \n\tquit - exit the application \n\tupdate - update the application \n\toffline - toggle offline mode"
defaultCommands = "\tlogin - log into a personal account for further access \n\tsignup - sign up for a new account"
userCommands = "\tlogout - log out of your account"
adminCommands = "\tboot - boot up automated scanning system \n\texec - execute a code snippet"
validStatuses = ["GOOD", "BROKEN", "MISSING", "FIXED", "BEYOND REPAIR", "DELETED"]
validTypes = ["MOTOR", "ESC", "CABLE", "REF SYSTEM"]

def getValidTypes():
    global validTypes
    return validTypes

def getValidStatuses():
    global validStatuses
    return validStatuses

#deletes last line in user file in case fail to push
def deleteLastLine():
    f = open('psuedo_db/users.csv', "r+")
    lines = f.readlines()
    lines.pop()
    f = open('psuedo_db/users.csv', "w+")
    f.writelines(lines)

#print funcs for convenience
def sysPrint(inputStr):
    print("SYSTEM >> " + inputStr)

def usrPrint(inputStr):
    if username == "":
        print("<< " + inputStr, end="")
        return
    print(username + " << " + inputStr, end="")

def toggleOffline():
    global offline
    offline = not offline
    return offline

#recursively looping main input function
def handleInput(inputStr):
    if inputStr == "h" or inputStr == "help":
        sysPrint("available commands:")
        print(universalCommands)
        if userStatus == "default":
            print(defaultCommands)
        elif userStatus == "user":
            print(userCommands)
        elif userStatus == "admin":
            print(userCommands)
            print(adminCommands)
    elif inputStr == "q" or inputStr == "quit":
        sysPrint("end command read. Shutting down application...")
        return False
    elif inputStr == "o" or inputStr == "offline":
        global offline
        if offline:
            offline = False
            sysPrint("System is now online")
        else:
            offline = True
            sysPrint("System is now offline")
    elif (inputStr == "l" or inputStr == "login") and userStatus == "default":
        loginUser()
    elif (inputStr == "s" or inputStr == "signup") and userStatus == "default":
        signUp()
    elif (inputStr == "l" or inputStr == "logout") and userStatus != "default":
        logout()
    elif (inputStr == "u" or inputStr == "update"):
        if githelper.gitPull() == False:
            sysPrint("Error: Could not connect to the database. Please check your connection and try again.")
            return
        else:
            sysPrint("Successfully updated! Please restart application immediately.")
            exit()
    elif (inputStr == "b" or inputStr == "boot") and userStatus == "admin":
        scanSystem()
    elif (inputStr == "e" or inputStr == "exec") and userStatus == "admin":
        executeCode()
    else:
        sysPrint("invalid command read. Please type in the command \"h\" or \"help\" for a list of available commands.")
    return True

#execute code command for debugging purposes
def executeCode():
    usrPrint("EXECUTE SCRIPT: ")
    try:
        exec(getRawInput(input()))
    except:
        sysPrint("Unable to execute command.")

#get raw input for string input
def getRawInput(myInput):
    while "\\n" in myInput:
        myInput = myInput[0:myInput.index("\\n")] + "\n" + myInput[myInput.index("\\n") + 2:len(myInput)]
    while "\\t" in myInput:
        myInput = myInput[0:myInput.index("\\t")] + "    " + myInput[myInput.index("\\t") + 2:len(myInput)]
    return myInput

def getDataBase():
    miniDB = []
    with open("psuedo_db/inventory.csv", "r") as f:
        miniDB = f.readlines()
    return miniDB

#handle scanning system
def scanSystem():
    global username
    global activityMessage
    activityMessage = username + " "
    if offline == False:
        if githelper.gitPull() == False:
            sysPrint("Error: Could not connect to the database. Please check your connection and try again.")
            scanSystem()
            return
    global fakeDatabase
    usrPrint("SCAN ID: ")
    code = input()
    bannerIDs = getBannerUsers()
    if code == "q" or code == "quit":
        return
    elif code == "listusers -o":
        for b in bannerIDs:
            print("\t\t" + b)
    elif code == "register" or code == "000000000":
        sysPrint("NOW REGISTERING ITEMS...")
        activityMessage += "registered items: "
        registerItems()
        if offline == False:
            pushInventory(username, "approved new registration for items", activityMessage)
    elif code == "update status" or code == "111111111":
        with open("psuedo_db/inventory.csv", "r") as f:
            fakeDatabase = f.readlines()
        sysPrint("NOW SCANNING ITEMS TO UPDATE")
        activityMessage += "updated items: "
        updateItems()
        with open("psuedo_db/inventory.csv", "w") as f:
                f.writelines(fakeDatabase)
        if offline == False:
            pushInventory(username, "approved status change for items", activityMessage)
    else:
        if code in bannerIDs:
            activityMessage = getUserFromBannerID(code) + " checked out/returned: "
            with open("psuedo_db/inventory.csv", "r") as f:
                fakeDatabase = f.readlines()
            sysPrint("NOW SCANNING ITEMS")
            scanItems(code)
            with open("psuedo_db/inventory.csv", "w") as f:
                f.writelines(fakeDatabase)
            if offline == False:
                pushInventory(getUserFromBannerID(code), "checked in/out new items", activityMessage)
            scanSystem()
            return
        sysPrint("SCANSYSTEM CRITICAL ERROR - COMMAND NOT RECOGNIZED")
    scanSystem()

def getUserFromBannerID(bannerID):
    with open("psuedo_db/users.csv", "r") as f:
        users = f.readlines()
        for u in users:
            line = u.split(",")
            if line[2] == bannerID:
                return line[0]
    return "invalid banner ID"

def pushInventory(user, action, logmsg):
    gitSuccess = githelper.gitCommit("RMI/psuedo_db/inventory.csv", user + " " + action)
    if gitSuccess:
        sysPrint("uploading to online database...please do not interrupt")
        gitSuccess = githelper.gitPush()
        gitSuccess = updateActivityLog(logmsg)
    if gitSuccess:
        sysPrint("Successfully pushed inventory changes!")
        return True
    else:
        sysPrint("Error occurred during upload. Please check for any network connection errors or git credential errors on this machine.")
        return False

def updateItems():
    global validStatuses
    global activityMessage
    newStatus = ""
    sysPrint("listening for status flag...")
    usrPrint("STATUS: ")
    code = input()
    if code == "update status" or code == "111111111":
        sysPrint("done updating status")
        activityMessage = activityMessage[0:len(activityMessage) - 2]
        return
    elif code in validStatuses:
        newStatus = code
    else:
        sysPrint("error: entered input is not a valid status. Please enter a valid status.")
        updateItems()
        return
    updateInventory(newStatus)
    updateItems()

def updateApp():
    if githelper.gitPull() == False:
        print("Error: Could not connect to the database. Please check your connection and try again.")
        return False
    else:
        print( "Successfully updated! Please restart application for changes to take place.")
        return True

def updateInventory(newStatus):
    global fakeDatabase
    global activityMessage
    sysPrint("listening for items...")
    usrPrint("ID: ")
    code = input()
    if code == newStatus:
        sysPrint("finished changing items to " + newStatus)
        return
    found = False
    for i in range(len(fakeDatabase)):
        d2 = fakeDatabase[i].split(",")
        if code == d2[0]:
            found = True
            activityMessage += code + ": " + (d2[3])[0:len(d2[3]) - 1] + "->" + newStatus + ", "
            d2[3] = newStatus + "\n"
            newline = ""
            for j in d2:
                newline += j.__str__() + ","
            fakeDatabase[i] = newline[0:len(newline) - 1]
            break;
    if found == False:
        sysPrint("error: item not registered and therefore status could not be changed.")
    updateInventory(newStatus)

def registerItems():
    global activityMessage
    sysPrint("listening for type of item to register...")
    usrPrint("REGISTER ID: ")
    code = input()
    if code == "register" or code == "000000000":
        sysPrint("done registering items!")
        return
    sysPrint("NOW REGISTERING " + code + " ITEMS")
    activityMessage += (code + "[")
    registerContents(code)
    activityMessage += "] "
    registerItems()

def registerContents(catagory):
    global activityMessage
    sysPrint("listening for next item to register...")
    usrPrint("ID: ")
    code = input()
    if code == catagory:
        activityMessage = activityMessage[0:len(activityMessage) - 2]
        sysPrint("done registering " + catagory + " items")
        return
    activityMessage += (code + ", ")
    with open("psuedo_db/inventory.csv", "a") as f:
        f.write(code + "," + catagory + ",HOME,GOOD\n")
    registerContents(catagory)

def scanItems(bannerID):
    global fakeDatabase
    global activityMessage
    sysPrint("listening for next item to check out...")
    usrPrint("ID: ")
    code = input()
    if code == bannerID:
        sysPrint("finished scanning items")
        activityMessage = activityMessage[0:len(activityMessage) - 2]
        return
    found = False
    for i in range(len(fakeDatabase)):
        d2 = fakeDatabase[i].split(",")
        if code == d2[0]:
            found = True
            activityMessage += code + ": "
            if d2[2] == bannerID:
                d2[2] = "HOME"
                activityMessage += (bannerID + "->HOME, ")
            else:
                d2[2] = bannerID
                activityMessage += ("HOME->" + bannerID + ", ")
            newline = ""
            for j in d2:
                newline += j.__str__() + ","
            fakeDatabase[i] = newline[0:len(newline) - 1]
            break;
    if found == False:
        sysPrint("error: item not registered and therefore could not be checked out.")
    scanItems(bannerID)

def getBannerUsers():
    bannerIDs = []
    with open("psuedo_db/users.csv", "r") as f:
        lines = f.readlines()
        for l in lines:
            items = l.split(",")
            bannerIDs.append(items[2])
    return bannerIDs

#log out of current account
def logout():
    global userStatus
    global username
    global password
    sysPrint("Are you sure you'd like to log out? (y/n)")
    usrPrint("")
    yOrN = input()
    while yOrN != "y" and yOrN != "n":
        sysPrint("invalid input recieved. Please type in \"y\" or \"n\".")
        usrPrint("")
        yOrN = input()
    if yOrN == "n":
        sysPrint("Canceled logout procedure.")
        return
    else:
        userStatus = "default"
        username = ""
        password = ""
    sysPrint("Successfully logged out! To log in again or as another user, please use the \"l\" or \"login\" command.")

def qtSignUp(fullname, email, bannerID, newUsername, newPassword, repeatPassword, adminCode):
    if newPassword != repeatPassword:
        return "ERROR:passwords do not match"

    newUser = [fullname, email, bannerID, newUsername, hashlib.md5(newPassword.encode()).hexdigest()]

    #handle verifying admin info
    if (hashlib.md5(adminCode.encode()).hexdigest()) != "d41d8cd98f00b204e9800998ecf8427e" and (hashlib.md5(adminCode.encode()).hexdigest()) != "87f37843c1e033f7efa88797fa9abe6f":
        return "ERROR:invalid admin code - please leave blank if signing up as a regular user."
    elif (hashlib.md5(adminCode.encode()).hexdigest()) == "87f37843c1e033f7efa88797fa9abe6f":
        adminCode = "admin"
    else:
        adminCode = "user"
    newUser.append(adminCode)

    #check for duplicate usernames or banner IDs and add to users.csv if possible
    dupUsr = False
    dupID = False
    with open("psuedo_db/users.csv", "r") as f:
        rows = f.readlines()
        for r in rows:
            row = r.split(",")
            if newUser[3] == row[3]:
                dupUsr = True
            if newUser[2] == row[2]:
                dupID = True
    
    if dupUsr:
        return "ERROR:entered username has already been used by another user. Unable to sign up with given information."
    elif dupID:
        return "ERROR:entered banner ID has already been used for another account. If you'd like to modify this account instead, login as this account or contact either Ben or Jason."
    else:
        with open("psuedo_db/users.csv", 'a+', newline='') as writefile:
            csv_writer = writer(writefile)
            csv_writer.writerow(newUser)
        activitySuccess = updateActivityLog("New user " + newUser[3] + " added to users database")
        gitSuccess = githelper.gitCommit("RMI/psuedo_db/users.csv", "New user " + newUser[3] + " added to users database")
        if gitSuccess and activitySuccess:
            gitSuccess = githelper.gitPush()
        if gitSuccess and activitySuccess:
            return "SUCCESS:Successfully signed up as a new user! Please verify you properly signed in by logging into the network. If any problems occur, please contact Ben or Jason."
        else:
            deleteLastLine()
            return "ERROR: unkown error occurred during upload. Please check for any network connection errors or git credential errors on this machine."

#sign up for a new account
def signUp():
    #make sure you are online
    global offline
    if offline == True:
        sysPrint("Error: you are in offline mode. You cannot sign up for a new account when offline.")
        return
    
    #check for connection with git pull and pull any possible changes
    if githelper.gitPull() == False:
        sysPrint("Error: Could not connect to the database. Please check your connection and try again.")
        return
    
    #create new user and ask for info
    newUser = []
    sysPrint("Please enter your full name here")
    usrPrint("name: ")
    newUser.append(input())
    sysPrint("Please enter your email here")
    usrPrint("email: ")
    newUser.append(input())
    sysPrint("Please enter your rose ID here")
    usrPrint("ID: ")
    newUser.append(input())
    sysPrint("Please enter your preferred username below")
    usrPrint("new username: ")
    newUser.append(input())
    sysPrint("Please enter a passcode")
    usrPrint("passcode: ")
    newUser.append((hashlib.md5(input().encode()).hexdigest()))
    sysPrint("Enter your admin code here if you have recieved one. Otherwise, leave blank.")
    usrPrint("admin code: ")
    adminCode = input()

    #handle verifying admin info
    if (hashlib.md5(adminCode.encode()).hexdigest()) != "d41d8cd98f00b204e9800998ecf8427e" and (hashlib.md5(adminCode.encode()).hexdigest()) != "14f1ff22fac48a7dfff8951d27a16b52":
        sysPrint("You have not submitted a correct admin code, continue signing up as a regular user? (y/n)")
        usrPrint("")
        yOrN = input()
        while yOrN != "y" and yOrN != "n":
            sysPrint("invalid input recieved. Please type in \"y\" or \"n\".")
            usrPrint("")
            yOrN = input()
        if yOrN == "n":
            sysPrint("Canceled signup procedure.")
            return
        else:
           adminCode = "user"
    elif (hashlib.md5(adminCode.encode()).hexdigest()) == "14f1ff22fac48a7dfff8951d27a16b52":
        adminCode = "admin"
    else:
        adminCode = "user"
    newUser.append(adminCode)

    #check for duplicate usernames or banner IDs and add to users.csv if possible
    dupUsr = False
    dupID = False
    with open("psuedo_db/users.csv", newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter = " ", quotechar = '|')
        rowStr = ""
        for row in reader:
            for r in row:
                rowStr += r
                rowStr += " "
            rowStr = rowStr[0:(len(rowStr) - 1)]
            rowlist = rowStr.split(',')
            if newUser[3] == rowlist[3]:
                dupUsr = True
            if newUser[2] == rowlist[2]:
                dupID = True

    #handle errors and upload to git if successful
    if dupUsr:
        sysPrint("Error: entered username has already been used by another user. Unable to sign up with given information.")
    elif dupID:
        sysPrint("Error: entered banner ID has already been used for another account. If you'd like to modify this account instead, login as this account or contact either Ben or Jason.")
    else:
        with open("psuedo_db/users.csv", 'a+', newline='') as writefile:
            csv_writer = writer(writefile)
            csv_writer.writerow(newUser)
        activitySuccess = updateActivityLog("New user " + newUser[3] + " added to users database")
        gitSuccess = githelper.gitCommit("RMI/psuedo_db/users.csv", "New user " + newUser[3] + " added to users database")
        if gitSuccess and activitySuccess:
            gitSuccess = githelper.gitPush()
        if gitSuccess and activitySuccess:
            sysPrint("Successfully signed up as a new user! Please verify you properly signed in by logging into the network. If any problems occur, please contact Ben or Jason.")
        else:
            deleteLastLine()
            sysPrint("Error occurred during upload. Please check for any network connection errors or git credential errors on this machine.")

def pushAll():
    gitSuccess = githelper.gitCommit("RMI/psuedo_db/users.csv", "New user updated")
    if gitSuccess:
        gitSuccess = pushInventory(username, "approved new registration for items", activityMessage)
    return gitSuccess
    
def searchUsers(str, username, email, bannerID, fullName, accountType):
    foundUsers = []
    dbUsers = []
    with open("psuedo_db/users.csv", "r") as f:
        dbUsers = f.readlines()
    for u in dbUsers:
        row = u.split(",")
        if ((username and str.casefold() in row[3].casefold()) or
            (email and str.casefold() in row[1].casefold()) or
            (bannerID and str.casefold() in row[2].casefold()) or
            (fullName and str.casefold() in row[0].casefold()) or
            (accountType and str.casefold() in row[5].casefold())):
            foundUsers.append(u)
    return foundUsers

def searchInventory(str, id, type, location, status):
    foundItems = []
    dbItems = []
    with open("psuedo_db/inventory.csv", "r") as f:
        dbItems = f.readlines()
    for i in dbItems:
        row = i.split(",")
        if ((id and str.casefold() in row[0].casefold()) or
            (type and str.casefold() in row[1].casefold()) or
            (location and str.casefold() in row[2].casefold()) or
            (status and str.casefold() in row[3].casefold())):
            foundItems.append(i)
    return foundItems

def updateActivityLog(log):
    today = datetime.now()
    numEntries = 0
    with open("../activitylog.txt", "r") as f:
        numEntries = len(f.readlines()) + 1
    with open("../activitylog.txt", "a") as f:
        f.write(log + "\n")
    gitSuccess = githelper.gitCommit("activitylog.txt", "entry #" + numEntries.__str__())
    if gitSuccess:
        gitSuccess = githelper.gitPush()
    return gitSuccess

def qtLoginUser(tmpUsername, tmpPassword):
    global username
    global password
    tmpPassword = (hashlib.md5(tmpPassword.encode()).hexdigest())
    foundUser = False
    with open("psuedo_db/users.csv" , newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter = ' ', quotechar = '|')
        for row in reader:
            if len(row) > 0:
                rowStr = ""
                for r in row:
                    rowStr += r
                    rowStr += " "
                rowStr = rowStr[0:(len(rowStr) - 1)]
                rowlist = rowStr.split(',')
                if len(rowlist) == 6:
                    if rowlist[3] == tmpUsername and rowlist[4] == tmpPassword:
                        username = tmpUsername
                        password = tmpPassword
                        userStatus = rowlist[5]
                        return "Success:" + rowlist[0] + ":" + userStatus
                    elif rowlist[3] == tmpUsername:
                        foundUser = True
        if foundUser:
            return "Error:wrong password for entered user. Are you sure you entered the correct password? If still unable to log in, please contact Ben or Jason."
        else:
            return "Error:unable to find entered user. Are you sure you entered the correct information? If still unable to log in, please contact Ben or Jason."

#login user func
def loginUser():
    global offline
    #check for connection with git pull and pull any possible changes
    if offline == False:
        if githelper.gitPull() == False:
            sysPrint("Error: Could not connect to the database. Please check your connection and try again.")
            return
    global username
    global password
    global userStatus
    sysPrint("Please enter your login information:")
    usrPrint("username: ")
    tmpUsername = input()
    usrPrint("password: ")
    tmpPassword = (hashlib.md5(input().encode()).hexdigest()) #from getpass import getpass password = getpass()
    foundUser = False
    with open("psuedo_db/users.csv" , newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter = ' ', quotechar = '|')
        for row in reader:
            if len(row) > 0:
                rowStr = ""
                for r in row:
                    rowStr += r
                    rowStr += " "
                rowStr = rowStr[0:(len(rowStr) - 1)]
                rowlist = rowStr.split(',')
                if len(rowlist) == 6:
                    if rowlist[3] == tmpUsername and rowlist[4] == tmpPassword:
                        username = tmpUsername
                        password = tmpPassword
                        userStatus = rowlist[5]
                        sysPrint("Welcome back " + rowlist[0] + "! You have been sucessfully logged in as a(n) " + userStatus + "!")
                        return
                    elif rowlist[3] == tmpUsername:
                        foundUser = True
        if foundUser:
            sysPrint("Error: wrong password for entered user. Are you sure you entered the correct password? If still unable to log in, please contact Ben or Jason.")
        else:
            sysPrint("Error: unable to find entered user. Are you sure you entered the correct information? If still unable to log in, please contact Ben or Jason.")

