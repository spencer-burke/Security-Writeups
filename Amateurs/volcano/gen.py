#!/usr/bin/python3
'''
min longlong: 2147483647
longlong max: 9223372036854775807
ulong max: 4294967295
prove max: 4294967295
prove min: 3
'''
'''
ANSWERS:
curr bear: 2147489606
curr volc: 2147549183
NEW ANSWERS:
curr bear: 2147535386
curr volc: 2147549183
'''

def check_bear(arg):
    if int(arg) & 1 == 0:
        if int(arg) % 3 == 2:
            if int(arg) % 5 == 1:
                if int(arg) + ((int(arg) - int(arg / 7) >> 1) + int(arg / 7) >> 2) * -7 == 3:
                    if arg % 0x6d == 0x37:
                        return 1
                    else:
                        return 0
                else:
                    return 0
            else:
                return 0
        else:
            return 0
    else:
        return 0 

def gen_bear(start):
    i = start
    while True:
        if check_bear(i) == 1:
            return i
        i += 1 

def check_volcano(arg): 
    curr = 0
    while arg != 0:
        curr = curr + (arg & 1) 
        arg = arg >> 1
    if curr < 0x11:
        return 0
    elif curr < 0x1b:
        return 1
    else:
        return 0

def gen_volcano(start):
    i = start
    while True:
        if check_volcano(i) == 1:
            return i
        i += 1

def get_length(arg):
    i = arg
    curr = 0
    while i != 0:
        curr += 1
        i = int(i/10)
    return curr

def check_is_same_length(arg1, arg2):
    if get_length(arg1) == get_length(arg2):
        return True

def mod_mangle(arg):
    i = arg
    curr = 0
    while i != 0:
        curr = curr + i % 10
        i = int(i/10)
    return curr

def check_mod_mangle(arg1, arg2):
    if (mod_mangle(arg1) == mod_mangle(arg2)):
        return True 

def gen_for_mod_mangle():
    # gen volcano version
    volcano_start = 2147483647
    bear_start = 2147483647
    curr_volcano = gen_volcano(volcano_start)
    curr_bear = gen_bear(bear_start)
    while True:
        if check_is_same_length(curr_volcano, curr_bear) == True and check_mod_mangle(curr_volcano, curr_bear) == True:
            print(f"bear = {curr_bear}")
            print(f"volcano = {curr_volcano}")
            break
        if bear_start > 9223372036854775807:
            print("maxed out")
            break
        bear_start += 1
        curr_bear = gen_bear(curr_bear+1)

def mangle_all_values(volcano_or_bear, prove, leet_value=0x1337):
    i = volcano_or_bear 
    curr = 1
    curr_mod = leet_value % prove
    while i != 0:
        if i & 1 != 0:
            curr = (curr * curr_mod) % prove
        curr_mod = (curr_mod * curr_mod) % prove
        i = i >> 1
    print(curr)
    return curr

def gen_for_mangle_all_values():
    bear_start = 2147535386
    volcano_start = 2147549183
    prove = 3
    while True:
        if mangle_all_values(bear_start, prove) == mangle_all_values(volcano_start, prove):
            print(f"prove = {prove}")
            break
        prove += 1

gen_for_mangle_all_values()