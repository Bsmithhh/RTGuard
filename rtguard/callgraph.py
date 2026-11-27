"""Walk calls reachable from a function, following functions defined in the TU."""
from clang.cindex import CursorKind

TIMEOUT_TARGETS = {
      "MsgSend", "MsgSendv", "MsgSendvs", "MsgSendnc", "MsgSendvnc", "MsgSendsv", "MsgSendsvnc",
      "MsgReceive", "MsgReceivev", "MsgReceivePulse",
      "InterruptWait", "SignalSuspend", "SignalWaitinfo", "SignalWaitinfoMask",
      "SyncCondvarWait", "SyncMutexLock", "SyncSemWait", "ThreadJoin",
      "pthread_barrier_wait",
  }

def reachable_calls(func):
    """Return the CALL_EXPR cursors reachable from func."""
    reached = []
    visited= set()
    todo = [func]
    while todo:
        current = todo.pop()
        if current in visited:
            continue
        visited.add(current)
        for node in current.walk_preorder():
            if node.kind == CursorKind.CALL_EXPR:
                reached.append(node)
                target = node.referenced
                if target and target.is_definition():
                    todo.append(target)
    return reached

def find_setup_in_loops(func):
    """Return setup calls (name_open, ConnectAttach, ChannelCreate) inside loops in func"""
    result = []
    spellings = ["name_open", "ConnectAttach", "ChannelCreate"]
    for node in func.walk_preorder():
        if node.kind == CursorKind.WHILE_STMT or node.kind == CursorKind.FOR_STMT or node.kind == CursorKind.DO_STMT:
            for child in node.walk_preorder():
                if child.kind == CursorKind.CALL_EXPR and child.spelling in spellings and child not in result:
                    result.append(child)
    return result

def find_disarmed_timeouts(func):
    """Return calls between TimerTimeout and the blocking call"""
    calls = [n for n in func.walk_preorder() if n.kind == CursorKind.CALL_EXPR]
    result = []
    for i, call in enumerate(calls):
        if call.spelling in ("TimerTimeout", "TimerTimeout_r", "timer_timeout"):
            if i + 1 < len(calls) and calls[i + 1].spelling.removesuffix("_r") not in TIMEOUT_TARGETS:
                result.append(calls[i+1])
    return result

def find_protected_calls(func):
    """Return blocking calls that come right after TimerTimeout(), so their timeout applies."""
    calls = [n for n in func.walk_preorder() if n.kind == CursorKind.CALL_EXPR]
    result = []
    for i, call in enumerate(calls):
        if call.spelling in ("TimerTimeout", "TimerTimeout_r", "timer_timeout"):
            if i + 1 < len(calls) and calls[i + 1].spelling.removesuffix("_r") in TIMEOUT_TARGETS:
                result.append(calls[i+1])
    return result
    