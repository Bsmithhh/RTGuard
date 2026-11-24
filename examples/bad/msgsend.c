#include <sys/neutrino.h>
#include <stdio.h>

int main(void) {
    int coid = 0;
    char msg[16] = "hi", reply[16];
    MsgSend(coid, msg, sizeof msg, reply, sizeof reply);
    printf("done\n");
    return 0;
}