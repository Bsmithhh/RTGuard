# RTGuard

RTGuard is a static analysis tool for C/C++ code written for QNX 8.0. It finds
calls inside time-critical threads that can make those threads miss their
deadlines, and suggests a fix for each one.

It runs on your development machine, not the target. It parses code with
Clang against QNX's own headers, so it understands the code the way a compiler
does instead of searching text.

Built for the QNX Global Hackathon (Developer Tooling & Host Tools).

## Example

```c
#include <stdio.h>
#include <unistd.h>

static void log_status(void) {
    printf("ok\n");
}

static void wait_a_bit(void) {
    log_status();
    sleep(1);
}

// rtguard: critical
void *control_loop(void *arg) {
    wait_a_bit();
    return 0;
}
```

```
helpers.c:10:5: warning: [RT-4] sleep suspends the thread, possibly longer than requested
  fix: wait on a periodic timer (timer_create() with a pulse) instead of sleeping
helpers.c:5:5: warning: [RT-2] printf does stdio/file I/O, which can block on the resource manager
  fix: log with slog2f() or write to a buffer and flush it from a non-critical thread
```

Both problems are hidden inside helper functions. RTGuard follows the calls
from `control_loop` down to them.

## How it works

1. **Parse** the file with libclang, using the QNX 8.0 headers (`rtguard/parse.py`).
2. **Find critical threads:** functions started by `pthread_create` with
   attributes set to `SCHED_FIFO` or `SCHED_RR`, plus any function marked
   `// rtguard: critical` (`rtguard/threads.py`).
3. **Walk the calls** reachable from each critical function, following helper
   functions defined in the same file (`rtguard/callgraph.py`).
4. **Match** each call against `rules.yaml` (`rtguard/rules.py`).
5. **Report** compiler-style warnings that editors and CI can parse
   (`rtguard/report.py`).

## Setup

Requires Python 3 and the [QNX SDP 8.0](https://www.qnx.com/products/everywhere/)
installed at `~/qnx800` (RTGuard reads the headers in
`~/qnx800/target/qnx/usr/include`).

```sh
git clone git@github.com:Bsmithhh/RTGuard.git
cd RTGuard
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Usage

The command-line entry point (`python -m rtguard <file>`) is in progress.
Until then, the pipeline can be run from Python:

```python
from rtguard.parse import parse
from rtguard.threads import find_critical
from rtguard.callgraph import reachable_calls
from rtguard.rules import load, match
from rtguard.report import warn

tu = parse("examples/bad/pthread_mixed.c")
rules = load("rules.yaml")
for func in find_critical(tu):
    for call in reachable_calls(func):
        rule = match(call, rules)
        if rule:
            warn(call, rule)
```

RTGuard treats a thread as critical when it is started with a real-time
scheduling policy:

```c
pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
pthread_create(&tid, &attr, control_loop, NULL);   // control_loop is critical
```

To mark a function as critical in any other case, put this comment on the
line directly above it:

```c
// rtguard: critical
void *control_loop(void *arg) { ... }
```

## Rules

Each rule links to the QNX 8.0 documentation it is based on.

| ID | Flags | Suggested fix | Docs |
|---|---|---|---|
| QNX-1 | `MsgSend()`, `MsgSendv()`: block until the server replies | Arm `TimerTimeout()` before the call | [MsgSend()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/msgsend.html) |
| QNX-2 | `MsgReceive()`, `MsgReceivev()`: block until a message arrives | Arm `TimerTimeout()` before the call | [MsgReceive()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/msgreceive.html) |
| QNX-3 | `InterruptWait()`: blocks until an interrupt occurs | Arm `TimerTimeout()` before the call | [InterruptWait()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/i/interruptwait.html) |
| RT-1 | `malloc`, `calloc`, `realloc`, `free`: unbounded allocation time | Allocate at init; reuse buffers or a fixed pool | [malloc()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/m/malloc.html) |
| RT-2 | `printf`, `fopen`, `fwrite` and other stdio: can block on a resource manager | `slog2f()`, or buffer and flush from a non-critical thread | [slog2f()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/slog2f.html) |
| RT-3 | `pthread_mutex_lock()`, `SyncMutexLock()`: block until the owner unlocks | Short critical sections, or `pthread_mutex_trylock()` with a fallback | [SyncMutexLock()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/s/syncmutexlock.html) |
| RT-4 | `sleep`, `usleep`, `delay`, `nanosleep`: suspend the thread | Wait on a periodic timer instead | [delay()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/d/delay.html) |
| RT-5 | `pthread_cond_wait()`, `sem_wait()`: block with no time limit | `pthread_cond_timedwait()`, `sem_timedwait()` | [pthread_cond_wait()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_cond_wait.html) |
| QNX-8 | `pthread_attr_setschedpolicy()` with `SCHED_FIFO`/`SCHED_RR` but no `PTHREAD_EXPLICIT_SCHED`: QNX ignores the policy and the thread inherits its creator's | Call `pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED)` | [pthread_attr_setschedpolicy()](https://www.qnx.com/developers/docs/8.0/com.qnx.doc.neutrino.lib_ref/topic/p/pthread_attr_setschedpolicy.html) |

### Planned

| ID | Flags |
|---|---|
| QNX-4 | A timeout on `MsgSend()` that won't fire because the server's channel uses `_NTO_CHF_UNBLOCK` |
| QNX-5 | `read()`/`write()`/`open()` on devices, which are messages to a resource manager |
| QNX-6 | Another kernel call between `TimerTimeout()` and the blocking call, which disarms the timeout |
| QNX-7 | `name_open()`, `ConnectAttach()`, `ChannelCreate()` inside a loop |

## Adding a rule

Add an entry to `rules.yaml`. No code changes are needed for rules that match
by function name:

```yaml
- id: RT-6
  functions: [some_function]
  message: what goes wrong
  fix: what to do instead
  doc: https://www.qnx.com/developers/docs/8.0/...
```

## Project layout

```
rtguard/
  parse.py       libclang setup with QNX flags
  threads.py     find critical thread functions
  callgraph.py   collect calls reachable from a function
  rules.py       load and match rules
  report.py      print warnings
rules.yaml       the rules
examples/        bad and good example programs
tests/           pytest suite
docker/          QNX qcc build for the examples
```
