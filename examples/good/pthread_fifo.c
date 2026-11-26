#include <pthread.h>
#include <sched.h>

static volatile int counter;

void *control_loop(void *arg) {
    counter++;
    return 0;
}

int main(void) {
    pthread_t rt;
    pthread_attr_t attr;

    pthread_attr_init(&attr);
    pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    pthread_create(&rt, &attr, control_loop, NULL);
    return 0;
}
