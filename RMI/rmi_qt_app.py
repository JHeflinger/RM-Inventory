from multiprocessing.dummy import active_children
import sys
import rmi
import githelper

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QDialogButtonBox,
    QLineEdit,
)

global numBtns
numBtns = 6

class BootWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.state = "start"
        self.desc = ""
        self.activityMessage = ""
        layout = QVBoxLayout()
        self.label = QLabel("IDLE")
        self.label.setStyleSheet("background-color: yellow")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont('Arial', 60))
        self.input = QLineEdit("")
        self.mainWindow = main_window
        self.input.returnPressed.connect(self.handleScanInput)
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        self.setLayout(layout)
        self.showMaximized()

    def handleScanInput(self):
        print(self.state)
        command = self.input.text()
        self.input.clear() #TODO: item info, user info
        if self.state == "start":
            if command == "quit":
                self.hide()
                self.mainWindow.show()
            elif command == "register":
                self.state = "pre-register"
                self.label.setText("SCAN ITEM TYPE TO REGISTER")
                self.label.setStyleSheet("background-color: orange")
        elif self.state == "pre-register":
            if command == "register":
                if not rmi.offline:
                    self.activityMessage = self.activityMessage[0:len(self.activityMessage) - 2] + " AS " + self.desc
                    rmi.pushInventory(rmi.username, "authorized registering items", self.activityMessage)
                self.state = "start"
                self.label.setText("IDLE")
                self.label.setStyleSheet("background-color: yellow")
                return
            if not rmi.offline:
                updated = rmi.updateApp()
                if not updated:
                    self.state = "start"
                    self.label.setText("ERROR COULD NOT CONNECT")
                    self.label.setStyleSheet("background-color: red")
                    return
            if command not in rmi.getValidTypes():
                self.label.setText("ERROR NOT VALID ITEM TYPE")
                self.label.setStyleSheet("background-color: red")
                return
            self.state = "register"
            self.activityMessage = "REGISTERED: "
            self.label.setText("LISTENING FOR " + command + " ITEMS")
            self.label.setStyleSheet("background-color: green")
            self.desc = command
        elif self.state == "register":
            if command == self.desc:
                self.state = "pre-register"
                self.label.setText("SCAN ITEM TYPE TO REGISTER")
                self.label.setStyleSheet("background-color: orange")
                return
            database = rmi.getDataBase()
            for row in database:
                if command == row.split(",")[0]:
                    self.label.setText("ERROR ITEM ALREADY REGISTERED")
                    self.label.setStyleSheet("background-color: red")
                    return
            with open("psuedo_db/inventory.csv", "a") as f:
                f.write(command + "," + self.desc + ",HOME,GOOD\n")
            self.activityMessage += (command + ", ")
            self.label.setText("REGISTERED " + command + " AS " + self.desc)
            self.label.setStyleSheet("background-color: green")

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RMI")
        self.setFixedSize(QSize(300, 50*numBtns))
        layout = QVBoxLayout()
        
        self.win = BootWindow(self)
        self.win.hide()

        self.loginStatus = QLabel("Guest")
        
        self.offlineButton = QPushButton("", self)
        self.offlineButton.setFixedSize(QSize(20, 20));
        self.offlineButton.setStyleSheet("background-color: green; border-radius: 10px;")
        self.offlineButton.clicked.connect(self.offline_clicked)
            
        headerbar = QHBoxLayout()
        headerbar.addWidget(self.loginStatus)
        headerbar.addWidget(self.offlineButton)
        
        self.loginBtn = QPushButton("Login")
        self.loginBtn.clicked.connect(self.login_clicked)
        self.logoutBtn = QPushButton("Logout")
        self.logoutBtn.clicked.connect(self.logout_clicked)
        self.logoutBtn.setEnabled(False)
        signupBtn = QPushButton("Sign Up")
        signupBtn.clicked.connect(self.signup_clicked)
        updateBtn = QPushButton("Update")
        updateBtn.clicked.connect(self.update_clicked)
        self.bootBtn = QPushButton("Boot System")
        self.bootBtn.clicked.connect(self.boot_clicked)
        self.bootBtn.setEnabled(False)
        
        layout.addLayout(headerbar)
        layout.addWidget(self.loginBtn)
        layout.addWidget(self.logoutBtn)
        layout.addWidget(signupBtn)
        layout.addWidget(updateBtn)
        layout.addWidget(self.bootBtn)
        
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    def boot_clicked(self, s):
        self.win.show()
        self.hide()

    def logout_clicked(self, s):
        self.loginStatus.setText("Guest")
        rmi.userStatus = "default"
        rmi.username = ""
        rmi.password = ""
        self.loginBtn.setEnabled(True)
        self.logoutBtn.setEnabled(False)
        self.bootBtn.setEnabled(False)
        notify = notifyDialog("You have been successfully logged out!")
        notify.exec()
        
    def login_clicked(self, s):
        dlg = LoginDialog()
        if dlg.exec():
            print("Success!")
            print(dlg.usernameBox.text())
            if not rmi.offline:
                self.offlineButton.setStyleSheet("background-color: blue; border-radius: 10px;")
                updated = rmi.updateApp()
                if not updated:
                    self.offlineButton.setStyleSheet("background-color: red; border-radius: 10px;")
                    rmi.toggleOffline()
                    dlg2 = updateDialog(False)
                    dlg2.exec()
                else:
                    self.offlineButton.setStyleSheet("background-color: green; border-radius: 10px;")
                    loggedIn = rmi.qtLoginUser(dlg.usernameBox.text(), dlg.passwordBox.text())
                    msg = loggedIn.split(":")
                    if msg[0] == "Error":
                        notify = notifyDialog("ERROR: " + msg[1])
                        notify.exec()
                    else:
                        self.loginStatus.setText(msg[2] + ": " + msg[1])
                        self.loginBtn.setEnabled(False)
                        self.logoutBtn.setEnabled(True)
                        notify = notifyDialog("Welcome back " + msg[1] + "! You have been sucessfully logged in as a(n) " + msg[2] + "!")
                        if msg[2] == "admin":
                            self.bootBtn.setEnabled(True)
                        notify.exec()
        else:
            print("Cancel!")
            
    def signup_clicked(self, s):
        dlg = SignupDialog()
        if dlg.exec():
            if not rmi.offline:
                self.offlineButton.setStyleSheet("background-color: blue; border-radius: 10px;")
                updated = rmi.updateApp()
                if not updated:
                    self.offlineButton.setStyleSheet("background-color: red; border-radius: 10px;")
                    rmi.toggleOffline()
                    dlg2 = updateDialog(False)
                    dlg2.exec()
                else:
                    self.offlineButton.setStyleSheet("background-color: green; border-radius: 10px;")
                    signedUp = rmi.qtSignUp(dlg.fullnameBox.text(), dlg.emailBox.text(), dlg.bannerIDBox.text(), dlg.usernameBox.text(), dlg.passwordBox.text(), dlg.confirmPasswordBox.text(), dlg.adminBox.text())
                    msg = signedUp.split(":")
                    if msg[0] == "ERROR":
                        notify = notifyDialog("ERROR: " + msg[1])
                        notify.exec()
                    else:
                        notify = notifyDialog(msg[1])
                        notify.exec()
        else:
            print("Cancel!")
            
    def update_clicked(self, s):
        self.offlineButton.setStyleSheet("background-color: blue; border-radius: 10px;")
        updated = rmi.updateApp()
        if not updated:
            self.offlineButton.setStyleSheet("background-color: red; border-radius: 10px;")
        else:
            self.offlineButton.setStyleSheet("background-color: green; border-radius: 10px;")
        dlg = updateDialog(updated)
        dlg.exec()
        
    def offline_clicked(self, s):
        rmi.toggleOffline()
        if rmi.offline:
            self.offlineButton.setStyleSheet("background-color: red; border-radius: 10px;")
        else:
            self.offlineButton.setStyleSheet("background-color: green; border-radius: 10px;")
    
class notifyDialog(QDialog):
    def __init__(self, msg):
        super().__init__()
        self.setWindowTitle("Notification")
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        message = QLabel(msg)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
    
class updateDialog(QDialog):
    def __init__(self, updated):
        super().__init__()
        self.setWindowTitle("Update Notification")
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        message = QLabel("Error: Could not connect to the database. Please check your connection and try again.")
        if updated:
            message = QLabel("Successfully updated! Please restart application for changes to take place.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
        
class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter your credentials here")
        QBtn = QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        usernameTitle = QLabel("Username:")
        self.usernameBox = QLineEdit("")
        passwordTitle = QLabel("Password:")
        self.passwordBox = QLineEdit("")
        self.passwordBox.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(usernameTitle)
        self.layout.addWidget(self.usernameBox)
        self.layout.addWidget(passwordTitle)
        self.layout.addWidget(self.passwordBox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class SignupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter your credentials here")
        QBtn = QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        fullnameTitle = QLabel("Full name:")
        self.fullnameBox = QLineEdit("")
        emailTitle = QLabel("Email:")
        self.emailBox = QLineEdit("")
        bannerIDTitle = QLabel("Banner ID:")
        self.bannerIDBox = QLineEdit("")
        usernameTitle = QLabel("Username:")
        self.usernameBox = QLineEdit("")
        passwordTitle = QLabel("Password:")
        self.passwordBox = QLineEdit("")
        confirmPasswordTitle = QLabel("Repeat password:")
        self.confirmPasswordBox = QLineEdit("")
        adminTitle = QLabel("Admin code (leave empty if regular user):")
        self.adminBox = QLineEdit("")
        self.adminBox.setEchoMode(QLineEdit.Password)
        self.passwordBox.setEchoMode(QLineEdit.Password)
        self.confirmPasswordBox.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(fullnameTitle)
        self.layout.addWidget(self.fullnameBox)
        self.layout.addWidget(emailTitle)
        self.layout.addWidget(self.emailBox)
        self.layout.addWidget(bannerIDTitle)
        self.layout.addWidget(self.bannerIDBox)
        self.layout.addWidget(usernameTitle)
        self.layout.addWidget(self.usernameBox)
        self.layout.addWidget(passwordTitle)
        self.layout.addWidget(self.passwordBox)
        self.layout.addWidget(confirmPasswordTitle)
        self.layout.addWidget(self.confirmPasswordBox)
        self.layout.addWidget(adminTitle)
        self.layout.addWidget(self.adminBox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

