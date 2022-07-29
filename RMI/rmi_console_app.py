from rmi import sysPrint, usrPrint, handleInput
appRunning = True
sysPrint("Welcome to RMI (Console app)! Enter a command to get started!")
while appRunning:
    usrPrint("")
    appRunning = handleInput(input())