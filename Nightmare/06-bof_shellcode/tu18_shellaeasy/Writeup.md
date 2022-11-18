# Challenge and Solution Theory
This is a basic buffer overflow with a jump to shellcode.
The challenge also gives a leak to the start of the stack frame the attacker can overwrite.
Also, there is a canary.
Overwriting the canary is simple, just place the value that is needed, because it is the same everytime.