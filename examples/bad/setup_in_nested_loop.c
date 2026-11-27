#include <sys/neutrino.h>
#include <sys/dispatch.h>

// rtguard: critical
void *nested(void *arg) {
    for (int i = 0; i < 3; i++) {
        do {
            int chid = ChannelCreate(0);
            ConnectAttach(0, 0, chid, _NTO_SIDE_CHANNEL, 0);
        } while (0);
    }
    return 0;
}
