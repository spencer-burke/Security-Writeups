# Challenge and Solution Theory
This is a buffer overflow challenge where you call a function, but there are two read's through scanf.
The first time you send input to the program, you can overwrite the amount read, and then you can send in a payload which will redirect program execution to the win function.