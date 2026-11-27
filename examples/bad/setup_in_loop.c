#include <sys/neutrino.h>
#include <sys/dispatch.h>

// rtguard: critical
void *bad_loop(void *arg) {
    while (1) {
        int coid = name_open("motor", 0);
        name_close(coid);
    }
    return 0;
}

// rtguard: critical
void *good_loop(void *arg) {
    int coid = name_open("motor", 0);
    for (int i = 0; i < 10; i++) {
        MsgSend(coid, 0, 0, 0, 0);
    }
    return 0;
}
