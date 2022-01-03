#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char buf[32];

int main(int argc, char* argv[], char* envp[]) {
    int fd = atoi( argv[1] ) - 0x1234;
    int len = 0;
    len = read(fd, buf, 32);

    if(!strcmp("LETMEWIN\n", buf)) {
        printf("inside code block\n");
    }


    return 0; 
}

