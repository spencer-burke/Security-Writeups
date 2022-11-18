# Challenge and Solution Theory
This is a jump to shellcode buffer overflow.
The only thing to keep in mind would be where the leak is pointing to.
Specifically, whether the leak points to the beginning of the stack or the end of it.
Also, do not point the program counter to nops.
It does not work.