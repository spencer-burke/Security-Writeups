# Challenge and Solution Theory
This is a stack overflow challenge where the attacker can jump to shellcode.
It gives the attacker a leak to the beginning of the stack frame they can overflow.
After this it is simply jumping to the pwntools generated shellcode.