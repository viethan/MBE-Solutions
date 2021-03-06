# MBE-Solutions
My thanks to ```RPISEC``` for making this course public for anyone to use. To see their course's resources, check here:
https://github.com/RPISEC/MBE

These lab exercises are some of my first ```pwn``` challenges. 
For every challenge solved there is a ```detailed explanation``` of the ```exploit``` and the ```step-by-step``` thought process that went behind it, including some of the difficulties that I had.

I hope this will help people who struggle with the exercises, because I did a little and felt that more detailed explanations would be incredibly helpful, especially for beginners.

A few things to note:
- I would recommend using ```fixenv``` for all the exercises before ```ASLR``` is turned on. This will make you so you don't have headaches with offset values, especially in ```lab3```. Don't worry, it's not cheating.
- It's best to solve most of the exercises with a ```python``` script. Therefore, some basic python knowledge is valuable. Don't worry about knowing everything, you'll pick up on the way as you advance thorugh the challenges and google.
- Speaking of ```python```, it's best to learn how to use ```pwntools```. It will ease your script crafting. Here's a crash course: [Auxy's Learn Pwntools Step by Step](https://laptrinhx.com/learn-pwntools-step-by-step-3291757783/). Consider making a cheat sheet.
- On ```Ubuntu```, before ```Xenial```, the ```libc base``` offset is constant from the main binary even with ```PIE``` enabled. Normally you wouldn't be able to do some of the things done in these labs, like calculating ```system()``` from and ```ELF function```. In modern pwn challenges, you need a libc leak to calculate a libc base address, stack leak to calculate a stack address etc etc.
