# Challenge Theory
This challenge is a reverse engineering challenge.
It gives a binary with not really any way to corrupt memory.
This challenge looks like a random fest, but it is not.
There is one specific part of the (decompiled)code which will allow the challenge to be solved.
# Working On and Solving the Challenge
Since this is a reversing challenge the first step would be to decompile the binary in something like Ghidra.
For the purposes of this writeup Ghidra will be used.
Taking a look at the code a few things stick out.
The main structure is really simple.
There are two functions in use.
The first is "main", this will then call the "\_main" function with one argument.
That is argument is "/dev/urandom/".
## Code for "main" Function
```
void main(void)
{
    int in_GS_OFFSET;
    undefined4 local_21;
    undefined4 local_1d;
    undefined4 local_19;
    undefined local_15;
    int local_14;
    undefined *local_c;

    local_c = &stack0x00000004;
    local_14 = *(int *)(in_GS_OFFSET + 0x14);
    setvbuf(stdout,(char *)0x0,2,0);
    setvbuf(stdin,(char *)0x0,2,0);
    setvbuf(stderr,(char *)0x0,2,0);
    local_21 = 0x7665642f;
    local_1d = 0x6172752f;
    local_19 = 0x6d6f646e;
    local_15 = 0;
    _main(&local_21);
        if (local_14 != *(int *)(in_GS_OFFSET + 0x14)) {
        /* WARNING: Subroutine does not return */
        __stack_chk_fail();
    }
    return;
}
```
The "local\_21" variable is a pointer the string "/dev/urandom".
This was found with a gdb debugging session.
## Code for "\_main" Function
```
void _main(char *param_1)
{
    FILE *pFVar1;
    int iVar2;
    int *piVar3;
    int in_GS_OFFSET;
    char local_b1;
    int local_a8 [4];
    uint local_98;
    char *local_14;
    int local_10;

    local_10 = *(int *)(in_GS_OFFSET + 0x14);
    iVar2 = 0x26;
    piVar3 = local_a8;
    while (iVar2 != 0) {
        iVar2 = iVar2 + -1;
        *piVar3 = 0;
        piVar3 = piVar3 + 1;
    }
    local_14 = param_1;
    puts(
    "Welcome to the final boss fight of my new indie game, Solid Rook. Your goal - predict thesame number as the final boss, Absolute Dice, 30 times in a row; she\'ll pick between 0 and20.\n"
    );
    while (local_a8[0] < 100) {
        local_a8[0] = local_a8[0] + 1;
        pFVar1 = fopen(local_14,"r");
        fread(local_a8 + 4,4,1,pFVar1);
        srand(local_98);
        printf("Enter your guess> ");
        __isoc99_scanf(&DAT_08048b2f,local_a8 + 3);
        local_a8[1] = rand();
        local_a8[1] = local_a8[1] % 0x15;
        local_a8[local_a8[0] % 0x21 + 5] = local_a8[3];
        if (local_a8[3] == local_a8[1]) {
            iVar2 = local_a8[2] + 1;
            local_a8[2] = iVar2;
            printf("Absolute Dice shrieks as your needle strikes a critical hit. (%d/50)\n",iVar2);
            if (0x1e < local_a8[2]) {
                printf("Absolute Dice shrieks as you take her down with a final hit.",iVar2);
                pFVar1 = fopen("flag.txt","r");
                iVar2 = fgetc(pFVar1);
                local_b1 = (char)iVar2;
                while (local_b1 != -1) {
                    putchar((int)local_b1);
                    iVar2 = fgetc(pFVar1);
                    local_b1 = (char)iVar2;
                }
                fclose(pFVar1);
            }
        }
        else {
            local_a8[2] = 0;
            printf("Absolute Dice scores a hit on you! (She had %d, you said %d)\n",local_a8[1], local_a8[3]);
        }
    }
    if (local_10 != *(int *)(in_GS_OFFSET + 0x14)) {
        /* WARNING: Subroutine does not return */
        __stack_chk_fail();
    }
    return;
}
```
This code is supposed to loop 100 times, but it does not.
It crashes after 32 passes.
This is because of this specific line.
## Code from "\_main" Function Which Causes a Crash
```
local_a8[local_a8[0] % 0x21 + 5] = local_a8[3];
```
This has an off-by-one error.
Since the array "local\_a8" has only 4 spaces, doing pointer arithmetic with the "+5" will actually cause a crash due to overwriting the next value.
Since the next value in the array is the value used to seed the random number this will overwrite the seed itself after 32 iterations.
A new value for the seed which will be constant.
To solve the challenge after 32 iterations simply input a new value.
The value used will be the pointer to the flag name converted to an int.
This value is "134515641".
After seeding this value the challenge only ever asks for 11.
This means the challenge can be solved because the number can be "guessed" the required 30 times. 
## Pwntools Solve Script
```
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This exploit template was generated via:
# $ pwn template --host 193.57.159.27 --port 35383 ./AbsoluteDice
from pwn import *

# Set up pwntools for the correct architecture
exe = context.binary = ELF('./AbsoluteDice')

# Many built-in settings can be controlled on the command-line and show up
# in "args".  For example, to dump all data sent/received, and disable ASLR
# for all created processes...
# ./exploit.py DEBUG NOASLR
# ./exploit.py GDB HOST=example.com PORT=4141
host = args.HOST or '193.57.159.27'
port = int(args.PORT or 35383)

#context.terminal = '[tmux'

def local(argv=[], *a, **kw):
    '''Execute the target binary locally'''
    if args.GDB:
    return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
    return process([exe.path] + argv, *a, **kw)

def remote(argv=[], *a, **kw):
    '''Connect to the process on the remote host'''
    io = connect(host, port)
    if args.GDB:
    gdb.attach(io, gdbscript=gdbscript)
    return io

def start(argv=[], *a, **kw):
    '''Start the exploit against the target.'''
    if args.LOCAL:
    return local(argv, *a, **kw)
    else:
    return remote(argv, *a, **kw)

# Specify your GDB script here for debugging
# GDB will be launched if the exploit is run via e.g.
# ./exploit.py GDB
gdbscript = '''
tbreak main
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================
# Arch:     i386-32-little
# RELRO:    Partial RELRO
# Stack:    Canary found
# NX:       NX enabled
# PIE:      No PIE (0x8048000)

io = start()
flag = b'134515641'

for _ in range(31):
      io.sendline(b'1')
io.sendline(flag)
io.sendline(flag)
correct_seed = io.recvline() # Parse this to get She had _ part
for _ in range(31):
    io.sendline(b'11')
print(correct_seed)

io.interactive()
```

