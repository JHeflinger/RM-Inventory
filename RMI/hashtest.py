import hashlib
adminCode = "XXXXX"
print((hashlib.md5(adminCode.encode()).hexdigest()))