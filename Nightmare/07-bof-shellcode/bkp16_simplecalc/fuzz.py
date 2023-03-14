#!/usr/bin/python3
import pwn
import sys
binary = "simplecalc"
pwn.context.binary = binary
pwn.context.encoding = "latin"
pwn.context.log_level = "debug"

payload = ""
padding = 24

def fuzz_crash(tinput):
    with pwn.process(binary) as io:
        io.sendline(str(tinput))
        io.sendline(str(5))
        io.wait_for_close()
        if (io.poll() != -11):
            fuzz_crash(tinput + 1)
        else:
            print(f"Fuzzing returned: {tinput}")
        
fuzz_crash(5)