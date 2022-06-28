print(">>Welcome to RMI Version 0.01 (Console side)! Please begin typing in commands below:")

#recursively looping main input function
def handleInput(inputStr):
    if inputStr == "h" or inputStr == "help":
        print(">> available commands:")
        print("\t<h/help> - brings up a list of available commands")
    else:
        print(">> invalid command read. Please type in the command \"h\" or \"help\" for a list of available commands.")
    handleInput(input())

#main functionality
handleInput(input())
