## What I'm building
RTGuard: a host-side static analysis tool for the QNX Global Hackathon
(Devpost, Developer Tooling & Host Tools category, deadline Dec 15, 2026).
It scans C/C++ code written for QNX 8.0 and flags calls that can make
time-critical threads miss deadlines, with a suggested fix for each.

## How it works
1. Parse C/C++ with libclang (Python), using QNX's real headers.
2. Find critical threads: functions passed to pthread_create whose thread
   uses SCHED_FIFO or SCHED_RR. Fallback: a `// rtguard: critical` comment.
3. Walk calls from those functions.
4. Match calls against rules in rules.yaml.
5. Print compiler-style warnings: file:line: warning: [RULE] ... / fix: ...

## Rules (each must link to its QNX 8.0 Library Reference page)
- QNX-1: MsgSend/MsgSendv block until reply -> suggest TimerTimeout()
- QNX-2: MsgReceive waits indefinitely (verify on 8.0 page)
- QNX-3: InterruptWait waits indefinitely (verify on 8.0 page)
- QNX-4: timeout may not unblock MsgSend if server channel uses _NTO_CHF_UNBLOCK
- RT-1..4: malloc/new, printf/file I/O, pthread_mutex_lock, sleep

## Environment
- macOS (Apple Silicon); QNX SDP 8.0 at ~/qnx800
- QNX headers: ~/qnx800/target/qnx/usr/include
- Parse flags: -nostdinc -I<headers> -D__QNXNTO__ -D__aarch64__
  -D__LITTLEENDIAN__ -Wno-pragma-pack
- Example programs compile with QNX's qcc inside Docker (teammate owns this)

## Planned layout
rtguard/{parse,threads,callgraph,rules,report}.py, rules.yaml,
examples/{bad,good}/, tests/, docker/

## Current status
- calls.py parses QNX code and finds MsgSend/printf with line numbers
- Next: first rule end to end, then critical-thread detection