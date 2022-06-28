import csv
print(">> Welcome to RMI Version 0.01 (Console side)! Please begin typing in commands below:")

#variables
global commands
global userStatus
global username
global password
userStatus = "default" #can be default, user, or admin
commands = {"help"      : "brings up a list of available commands", 
            "quit"      : "exit the application",
            "login"     : "log into a personal account for further access",
            "signup"    : "sign up for a new account"}

#recursively looping main input function
def handleInput(inputStr):
    if inputStr == "h" or inputStr == "help":
        print(">> available commands:")
        for str in commands:
            print("\t" + str[0:1] + "/" + str + " - " + commands[str])
    elif inputStr == "q" or inputStr == "quit":
        print(">> end command read. Shutting down application...")
        return
    elif inputStr == "l" or inputStr == "login":
        loginUser()
    else:
        print(">> invalid command read. Please type in the command \"h\" or \"help\" for a list of available commands.")
    print("<< ", end="")
    handleInput(input())

def loginUser():
    print(">> Please enter your login information:")
    print("<< username: ", end="")
    username = input()
    print("<< password: ", end="")
    password = input() #from getpass import getpass password = getpass()
    with open("users.csv" , newline = '') as csvfile:
        reader = csv.reader(csvfile, delimiter = ' ', quotechar = '|')
        for row in reader:
            print(row)

#main functionality
print("<< ", end="")
handleInput(input())
