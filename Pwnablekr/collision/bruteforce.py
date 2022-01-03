#!/usr/bin/python3
import sys
import subprocess

"""
This script does not work.
It is not a reasonable solution.
It might not even put in the right data.
"""

def pad(arg):
    res = ""
    if(len(str(arg)) < 20):
        diff = 20 - len(str(arg))
        res = str(arg)
        for x in range(diff-1):
            res = "0" + res
    if(res != ""):
        return res
    else:
        return arg 

def main():
    num = 0;
    with open("log.out", "a") as f:
        for x in range(99999999999999999999):
            f.write( (subprocess.check_output( ["./run", str(pad(x))] )).decode("utf-8") ) 

if __name__ == "__main__":
    main()

