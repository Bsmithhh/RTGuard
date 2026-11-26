#include <pthread.h>
#include <sched.h>
#include <stdio.h>

void *control_loop(void *arg) {
    printf("tick\n");
    return 0;
}

void *logger(void *arg) {
    printf("log\n");
    return 0;
}

int main(void) {
    pthread_t rt, bg;
    pthread_attr_t attr;

    pthread_attr_init(&attr);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    pthread_create(&rt, &attr, control_loop, NULL);

    pthread_create(&bg, NULL, logger, NULL);
    return 0;
}
