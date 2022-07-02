import csv
from csv import writer
import hashlib
print("SYSTEM >> Welcome to RMI Version 0.01 (Console side)! Please begin typing in commands below:")

#variables
global universalCommands
global defaultCommands
global userCommands
global adminCommands
global userStatus
global username
global password
userStatus = "default" #can be default, user, or admin
username = ""
password = ""
universalCommands = "\thelp - brings up a list of available commands \n\tquit - exit the application \n\tupdate - update the application"
defaultCommands = "\tlogin - log into a personal account for further access \n\tsignup - sign up for a new account"
userCommands = "\tlogout - log out of your account"
adminCommands = "\tmanage - manage system users"

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
    elif (inputStr == "l" or inputStr == "login") and userStatus == "default":
        loginUser()
    elif (inputStr == "s" or inputStr == "signup") and userStatus == "default":
        signUp()
    elif (inputStr == "l" or inputStr == "logout") and userStatus != "default":
        logout()
    else:
        sysPrint("invalid command read. Please type in the command \"h\" or \"help\" for a list of available commands.")
    usrPrint("")
    handleInput(input())

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
    if dupUsr:
        sysPrint("Error: entered username has already been used by another user. Unable to sign up with given information.")
    elif dupID:
        sysPrint("Error: entered banner ID has already been used for another account. If you'd like to modify this account instead, login as this account or contact either Ben or Jason.")
    else:
        with open("psuedo_db/users.csv", 'a+', newline='') as writefile:
            csv_writer = writer(writefile)
            csv_writer.writerow(newUser)
        sysPrint("Successfully signed up as a new user! Please verify you properly signed in by logging into the network. If any problems occur, please contact Ben or Jason.")

#login user func
def loginUser():
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
