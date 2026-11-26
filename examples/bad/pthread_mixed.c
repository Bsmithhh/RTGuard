#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <unistd.h>

// rtguard: critical
void *sensor(void *arg) { sleep(1); return 0; }
void *motor(void *arg) { printf("m\n"); return 0; }
void *ui(void *arg) { printf("ui\n"); return 0; }

int main(void) {
    pthread_t a, b, c;
    pthread_attr_t rr, normal;
    pthread_attr_init(&rr);
    pthread_attr_setschedpolicy(&rr, SCHED_RR);
    pthread_attr_init(&normal);
    pthread_attr_setschedpolicy(&normal, SCHED_OTHER);
    pthread_create(&a, &rr, sensor, NULL);
    pthread_create(&b, &rr, motor, NULL);
    pthread_create(&c, &normal, ui, NULL);
    return 0;
}
