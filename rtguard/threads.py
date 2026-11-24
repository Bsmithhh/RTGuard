"""Find critical threads: pthread_create targets using SCHED_FIFO/SCHED_RR,
or functions marked with a `// rtguard: critical` comment."""


def find_critical(tu):
    """Return the function cursors that run as critical threads."""
    raise NotImplementedError
