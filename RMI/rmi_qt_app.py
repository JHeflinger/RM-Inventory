import sys
import rmi
import githelper

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QDialog,
    QDialogButtonBox,
    QLineEdit
)

global numBtns
numBtns = 4

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RMI")
        self.setFixedSize(QSize(200, 40*numBtns))
        layout = QVBoxLayout()
        loginBtn = QPushButton("Login")
        loginBtn.clicked.connect(self.login_clicked)
        signupBtn = QPushButton("Sign Up")
        signupBtn.clicked.connect(self.signup_clicked)
        updateBtn = QPushButton("Update")
        updateBtn.clicked.connect(self.update_clicked)
        bootBtn = QPushButton("Boot System")
        bootBtn.setEnabled(False)
        layout.addWidget(loginBtn)
        layout.addWidget(signupBtn)
        layout.addWidget(updateBtn)
        layout.addWidget(bootBtn)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
    def login_clicked(self, s):
        dlg = LoginDialog()
        if dlg.exec():
            print("Success!")
        else:
            print("Cancel!")
            
    def signup_clicked(self, s):
        dlg = SignupDialog()
        if dlg.exec():
            print("Success!")
        else:
            print("Cancel!")
            
    def update_clicked(self, s):
        successPull = githelper.gitPull()
        notifyMessage = ""
        if successPull:
            notifyMessage = "Update successfully installed! Please restart the app for changes to take effect."
        else:
            notifyMessage = "Error connecting to server. Please check your internet connection and try again."
        dlg = notifyDialog(notifyMessage)
        dlg.exec()
        
class notifyDialog(QDialog):
    def __init__(self, notifyMessage):
        super().__init__()
        self.setWindowTitle("Update Notification")
        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        message = QLabel(notifyMessage)
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
        usernameBox = QLineEdit("")
        passwordTitle = QLabel("Password:")
        passwordBox = QLineEdit("")
        passwordBox.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(usernameTitle)
        self.layout.addWidget(usernameBox)
        self.layout.addWidget(passwordTitle)
        self.layout.addWidget(passwordBox)
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
        fullnameBox = QLineEdit("")
        emailTitle = QLabel("Email:")
        emailBox = QLineEdit("")
        bannerIDTitle = QLabel("Banner ID:")
        bannerIDBox = QLineEdit("")
        usernameTitle = QLabel("Username:")
        usernameBox = QLineEdit("")
        passwordTitle = QLabel("Password:")
        passwordBox = QLineEdit("")
        confirmPasswordTitle = QLabel("Repeat password:")
        confirmPasswordBox = QLineEdit("")
        adminTitle = QLabel("Admin code (leave empty if regular user):")
        adminBox = QLineEdit("")
        adminBox.setEchoMode(QLineEdit.Password)
        passwordBox.setEchoMode(QLineEdit.Password)
        confirmPasswordBox.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(fullnameTitle)
        self.layout.addWidget(fullnameBox)
        self.layout.addWidget(emailTitle)
        self.layout.addWidget(emailBox)
        self.layout.addWidget(bannerIDTitle)
        self.layout.addWidget(bannerIDBox)
        self.layout.addWidget(usernameTitle)
        self.layout.addWidget(usernameBox)
        self.layout.addWidget(passwordTitle)
        self.layout.addWidget(passwordBox)
        self.layout.addWidget(confirmPasswordTitle)
        self.layout.addWidget(confirmPasswordBox)
        self.layout.addWidget(adminTitle)
        self.layout.addWidget(adminBox)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()

