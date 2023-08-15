# Challenge Theory
This is a keygen challenge, but there is not one singular "key" that meets all of the requirements\(to my knowledge\).
Solving this is a case of reimplementing the checks, and then generating numbers which pass the checks.
The only problem with this is there are multiple checks, and the input has to pass through all of them.
## Important Source Code
```c
  user_input_bear = 0;
  __isoc99_scanf("%llu",&user_input_bear);
  mangle_result = mangle_is_bear(user_input_bear);
  if (mangle_result == '\x01') {
    printf("Give me a volcano: ");
    user_input_volcano = 0;
    __isoc99_scanf("%llu",&user_input_volcano);
    mangle_result = mangle_is_volcano(user_input_volcano);
    if (mangle_result == '\x01') {
      printf("Prove to me they are the same: ");
      user_input_prove = 0;
      leet_value = 0x1337;
      __isoc99_scanf("%llu",&user_input_prove);
      if (((user_input_prove & 1) == 0) || (user_input_prove == 1)) {
        puts("That\'s not a valid proof!");
        uVar1 = 1;
      }
      else {
        mangled_volcano = is_same_length(user_input_volcano);
        mangled_bear = is_same_length(user_input_bear);
        if (mangled_volcano == mangled_bear) {
          mangled_volcano = mangle_bear_and_volcano_with_mod(user_input_volcano);
          mangled_bear = mangle_bear_and_volcano_with_mod(user_input_bear);
          if (mangled_volcano == mangled_bear) {
            mangled_volcano = mangle_all_values(leet_value,user_input_volcano,user_input_prove);
            mangled_bear = mangle_all_values(leet_value,user_input_bear,user_input_prove);
            if (mangled_volcano == mangled_bear) {
              puts("That looks right to me!");
              local_b0 = fopen("flag.txt","r");
              fgets(local_a8,0x80,local_b0);
              puts(local_a8);
              uVar1 = 0;
              goto exit_label;
            }
          }
        }
        puts("Nope that\'s not right!");
        uVar1 = 1;
      }
    }
    else {
      puts("That doesn\'t look like a volcano!");
      uVar1 = 1;
    }
  }
  else {
    puts("That doesn\'t look like a bear!");
    uVar1 = 1;
  }
```
After reverse engineering it to get to recreate the source code above, all of the checks need to be reimplemented.
The last piece of relevant information is the maximum and mininum size of a c ulong max variable.
The program asks for two of those as user input.
So that actually provides the range of values for the challenge.
# Working on the Challenge
The first check is the first volcano check.
## Volcano Check
```python
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
```
Then another function can be implemented to generate a value, and check if it is valuable.
## Volcano Generation
```python
def gen_volcano(start):
    i = start
    while True:
        if check_volcano(i) == 1:
            return i
        i += 1
``` 
The program also asks for a bear, so that has to be generated as well.
## Bear Check
```python
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
```
## Bear Generation
```python
def gen_bear(start):
    i = start
    while True:
        if check_bear(i) == 1:
            return i
        i += 1 
```
Continuing forward with the different checks the next set wants the values to be of equal length.
To accomplish this, the first valid volcano value was used, and then different bear values were generated.
## Mod Mangle
```python
def mod_mangle(arg):
    i = arg
    curr = 0
    while i != 0:
        curr = curr + i % 10
        i = int(i/10)
    return curr
``` 
Now, it's time to pull all of these things together into one final check.
## Mod Mangle Generation
```python
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
```
After this the program checks for one final aspect.
It mangles the values with 0x1337
## Mangle All Values
```python
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
```
## Generation for Mangle All Values
```python
def gen_for_mangle_all_values():
    bear_start = 2147535386
    volcano_start = 2147549183
    prove = 3
    while True:
        if mangle_all_values(bear_start, prove) == mangle_all_values(volcano_start, prove):
            print(f"prove = {prove}")
            break
        prove += 1
```
# Full Solution
The full solution isn't quite implemented.
Since it was being run as it was built.
The final check and generation used the values from the first few tests.
The final script looks like this.
## Final Solution Script
```python
#!/usr/bin/python3

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
```