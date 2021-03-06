## lab4C

Looking over the source code of this file, we can see that the ```lab4C``` binary opens the file with the flag, reads and stores it in a variable called ```real_pass[PASS_LEN]```.

Afterwards the program asks us for our username and the password. If both correct, it will spawn a shell for us. If not, it will perform ```printf(username);```, which is vulnerable to format strings attacks.

We know that the stack grows towards lower addresses, and that the local variables are also on the stack. Using the ```%x``` format parameter we can scan the stack to try and read the string with our flag.

```c
char username[100] = {0};
char real_pass[PASS_LEN] = {0};
char in_pass[100] = {0};
FILE *pass_file = NULL;
int rsize = 0;
```

Because of the way the variables are stored on the stack, we will see the last ones first. 
Note: Our ```username``` can only be 100 characters. We will scan the stack using ```%08x.``` . Since that is a string of 5 chars, with this method we will scan about 20 4byte values on the stack.

```bash
lab4C@warzone:/tmp/transcen/lab4$ /levels/lab04/lab4C
===== [ Secure Access System v1.0 ] =====
-----------------------------------------
- You must login to access this system. -
-----------------------------------------
--[ Username: %08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.%08x.
--[ Password: BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
-----------------------------------------
bffff482.0000001e.0804a008.42420000.42424242.42424242.42424242.42424242.42424242.42424242.42424242.42424242.42424242.42424242.42424242.42424242.42424242.42424242.42424242. does not have access!
```

As we guessed, we first see ```rsize = 0000001e```, the ```file descriptor``` and ```in_pass[100]``` values. By knowing that our flag is 30 characters (NULL included), and that our input password is 100 characters, we can calculate the indexes where the ```lab4B``` pass is stored.

```bash
lab4C@warzone:/tmp/transcen/lab4$ /levels/lab04/lab4C
===== [ Secure Access System v1.0 ] =====
-----------------------------------------
- You must login to access this system. -
-----------------------------------------
--[ Username: %29$08x.%30$08x.%31$08x.%32$08x.%33$08x.%34$08x.%35$08x.%36$08x
--[ Password: 
-----------------------------------------
75620000.74315f37.7334775f.625f376e.33745572.7230665f.62343363.00216531 does not have access!
```

Since memory is little endian, we have to reverse the byte order, change from hex to ASCII and so we will have our flag!
```
Flag: bu7_1t_w4sn7_brUt3_f0rc34b1e!
```

## lab 4B


In this challenge, we get to take advantage of the format string vulnerability once again. We are allowed to insert a shellcode in a buffer, but we cannot overflow it. One important aspect of this shellcode is that if it has any capital letters, they will get changed to their lower equivalents. The hex codes for letter from ```A``` to ```Z``` are from ```0x41``` to ```0x5A```.

If we look through our shellcode, we can see that the ```push e*x``` instructions are between ```0x50``` and ```0x59```, therefore we cannot use any of them. No worries, we will construct a shellcode to get around this, by substituting the ```push eax``` instruction with ```sub esp, 4 ; mov [esp], eax```.

Using ```checksec```, we see that ```RELRO``` is disabled, so therefore we can modify the ```dtors``` table or modify the ```global offset table```. We will choose the former. We will modify the address ```0x080498ac``` to point to our shellcode, which will have a NOP sled for safe measure.

We will perform two short writes, one at ```0x080498ac``` and one at ```0x080498ae```. Since the middle of our shellcode is at address ```0xbffff671```, we will change the dtors entry to that value.

We begin our payload with the addresses were we will make the 2 short writes. We can see that they are the ```6th``` and ```7th``` element on the stack. By calculating the length of our shellcode, the length of the NOPSLED and adding 8, we can calculate the number of bytes we need in order to perform the correct operations.

```bash
lab4B@warzone:/levels/lab04$ python expl4B.py
cat ~lab4A/.pass
fg3ts_d0e5n7_m4k3_y0u_1nv1nc1bl3
```

## lab4A

The program seems to request a ```command line argument```. It then open a log file which is at ```./backups/.log```. If it doesn't exist, it will exit. Using the log_wrapper function, it concatenates the string - ```Starting back up: ``` with the our ```argv[1]```. We can see that the snprintf function is vulnerable to a format string attack.

Before we begin to construct our payload, let's continue reading the source code. After the ```log_wrapper``` call, the binary will open the file with the name as our ```argv[1]```, the ```source```. If it doesn't exist, it will exit. Since our log_wrapper function has the vulnerability and is before this call, we don't necessarily need to do this. 

It will then create a string - ```./backups/argv[1]```, and attempt to open that file, our ```dest```. If it doesn't exist, it will create it and will give it a few permissions.

Afterwards it will copy byte after byte from ```source```, the original file, to ```dest```, the backup file created in ```./backups/ directory```.
So, at the end, it is a simple program that makes a backup of a file in ```./backups/``` and keeps a hidden log ```file```. 

In order for the program to run as long as our exploit needs it to run, we have to make sure that the ```./backups/.log``` file exists. As such, using the ```os``` and ```shutil``` modules, we will create the directory and hidden file, launch our exploit, and delete them at the end.

Using ```checksec```, we can that ```RELRO``` is fully enabled, so we can't use ```global offset``` or ```dtors``` tables. Therefore, we need to change ```RET``` to go our ```shellcode```.

```bash
lab4B@warzone:/levels/lab04$ python expl4A.py
cat ~lab4end/.pass
1t_w4s_ju5t_4_w4rn1ng
```
