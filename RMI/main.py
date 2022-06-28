import csv
print("SYSTEM >> Welcome to RMI Version 0.01 (Console side)! Please begin typing in commands below:")

#variables
global commands
global userStatus
global username
global password
userStatus = "default" #can be default, user, or admin
username = ""
password = ""
commands = {"help"      : "brings up a list of available commands", 
            "quit"      : "exit the application",
            "login"     : "log into a personal account for further access",
            "signup"    : "sign up for a new account"}

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
        for str in commands:
            print("\t" + str[0:1] + "/" + str + " - " + commands[str])
    elif inputStr == "q" or inputStr == "quit":
        sysPrint("end command read. Shutting down application...")
        return
    elif inputStr == "l" or inputStr == "login":
        loginUser()
    else:
        sysPrint("invalid command read. Please type in the command \"h\" or \"help\" for a list of available commands.")
    usrPrint("")
    handleInput(input())

#login user func
def loginUser():
    global username
    global password
    global userStatus
    sysPrint("Please enter your login information:")
    usrPrint("username: ")
    tmpUsername = input()
    usrPrint("password: ")
    tmpPassword = input() #from getpass import getpass password = getpass()
    foundUser = False
    with open("users.csv" , newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter = ' ', quotechar = '|')
        for row in reader:
            if len(row) > 0:
                rowlist = row[0].split(',')
                if len(rowlist) == 3:
                    if rowlist[0] == tmpUsername and rowlist[1] == tmpPassword:
                        username = tmpUsername
                        password = tmpPassword
                        userStatus = rowlist[2]
                        sysPrint("Welcome back " + username + "! You have been sucessfully logged in as a(n) " + userStatus + " user!")
                        return
                    elif rowlist[0] == tmpUsername:
                        foundUser = True
        if foundUser:
            sysPrint("Error: wrong password for entered user. Are you sure you entered the correct password? If still unable to log in, please contact an administrator.")
        else:
            sysPrint("Error: unable to find entered user. Are you sure you entered the correct information? If still unable to log in, please contact an administrator.")

#main functionality
usrPrint("")
handleInput(input())
