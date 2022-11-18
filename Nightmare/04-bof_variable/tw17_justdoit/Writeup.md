# Challenge Theory and Solution
This is a buffer overflow challenge with somewhat of a twist.
The way to solve this challenge, is to overwrite the fail message, with the address of the flag instead.
Since the flag has a space in memory, you can the fail message address with the flag, and print the flag instead.