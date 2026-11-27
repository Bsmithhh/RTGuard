#include <sys/neutrino.h>
#include <stdio.h>
#include <string.h>

static char msg[16], reply[16];

// rtguard: critical
void *good(void *arg) {
    int coid = 1;
    TimerTimeout(CLOCK_MONOTONIC, _NTO_TIMEOUT_SEND | _NTO_TIMEOUT_REPLY, NULL, NULL, NULL);
    MsgSend(coid, msg, strlen(msg), reply, sizeof reply);
    return 0;
}

// rtguard: critical
void *bad(void *arg) {
    int coid = 1;
    TimerTimeout(CLOCK_MONOTONIC, _NTO_TIMEOUT_SEND | _NTO_TIMEOUT_REPLY, NULL, NULL, NULL);
    printf("sending\n");
    MsgSend(coid, msg, sizeof msg, reply, sizeof reply);
    return 0;
}
