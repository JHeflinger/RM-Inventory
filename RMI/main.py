import csv
from csv import writer
import hashlib
import githelper
print("SYSTEM >> Welcome to RMI Version 0.01 (Console side)! Please begin typing in commands below:")

#variables
global universalCommands
global defaultCommands
global userCommands
global adminCommands
global userStatus
global username
global password
global offline
offline = False
userStatus = "default" #can be default, user, or admin
username = ""
password = ""
universalCommands = "\thelp - brings up a list of available commands \n\tquit - exit the application \n\tupdate - update the application \n\toffline - toggle offline mode"
defaultCommands = "\tlogin - log into a personal account for further access \n\tsignup - sign up for a new account"
userCommands = "\tlogout - log out of your account"
adminCommands = "\tboot - boot up automated scanning system \n\texec - execute a code snippet"

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
        return
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
    usrPrint("")
    handleInput(input())

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

#handle scanning system
def scanSystem():
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
        registerItems()
    else:
        if code in bannerIDs:
            scanItems(code)
            scanSystem()
            return
        sysPrint("SCANSYSTEM CRITICAL ERROR - COMMAND NOT RECOGNIZED")
    scanSystem()

def registerItems():
    sysPrint("listening for type of item to register...")
    usrPrint("REGISTER ID: ")
    code = input()
    if code == "register" or code == "000000000":
        sysPrint("done registering items!")
        return
    sysPrint("NOW REGISTERING " + code + " ITEMS")
    registerContents(code)
    registerItems()

def registerContents(catagory):
    sysPrint("listening for next item to register...")
    usrPrint("ID: ")
    code = input()
    if code == catagory:
        sysPrint("done registering " + catagory + " items")
        return
    with open("psuedo_db/inventory.csv", "a") as f:
        f.write(code + "," + catagory + ",HOME,GOOD\n")
    registerContents(catagory)

def scanItems(bannerID):
    sysPrint("NOW SCANNING ITEMS")

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
        gitSuccess = githelper.gitCommit("RMI/psuedo_db/users.csv", "New user " + newUser[3] + " added to users database")
        if gitSuccess:
            gitSuccess = githelper.gitPush()
        if gitSuccess:
            sysPrint("Successfully signed up as a new user! Please verify you properly signed in by logging into the network. If any problems occur, please contact Ben or Jason.")
        else:
            deleteLastLine()
            sysPrint("Error occurred during upload. Please check for any network connection errors or git credential errors on this machine.")

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

#main functionality
usrPrint("")
handleInput(input())
