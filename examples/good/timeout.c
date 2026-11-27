#include <sys/neutrino.h>
#include <string.h>

static char msg[16], reply[16];

// rtguard: critical
void *send_with_timeout(void *arg) {
    int coid = 1;
    TimerTimeout(CLOCK_MONOTONIC, _NTO_TIMEOUT_SEND | _NTO_TIMEOUT_REPLY, NULL, NULL, NULL);
    MsgSend(coid, msg, strlen(msg), reply, sizeof reply);
    return 0;
}
