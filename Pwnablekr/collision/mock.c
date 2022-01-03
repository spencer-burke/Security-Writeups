#include <stdio.h>
#include <string.h>
unsigned long hashcode = 0x21DD09EC;
unsigned long check_password(const char* p){
    int* ip = (int*)p;
    int i;
    int res=0;
    for(i=0; i<5; i++){
        res += ip[i];
    }
    return res;
}

unsigned long reverse_hash_code(const char* p) {
    int* ip = (int*)p;
    int i;
    int res = 0x21DD09EC; 
    for(i=0; i<5; i++){
        res -= ip[i];
    }
    return res;
}

int main(int argc, char* argv[]){
    if(hashcode == check_password( argv[1] )){
           printf("Correct passcode: %d\n", check_password( argv[1] ));
    }
    else{
       printf("wrong passcode\n");
    }
}

