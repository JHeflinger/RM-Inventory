import hashlib
adminCode = "80085"
print((hashlib.md5(adminCode.encode()).hexdigest()))