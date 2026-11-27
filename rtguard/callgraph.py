"""Walk calls reachable from a function, following functions defined in the TU."""
from clang.cindex import CursorKind


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
    """Return setup calls (name_open, ConnectAttach, ChannelCreate) inside loops reachable from func."""
    result = []
    spellings = ["name_open", "ConnectAttach", "ChannelCreate"]
    for node in func.walk_preorder():
        if node.kind == CursorKind.WHILE_STMT or node.kind == CursorKind.FOR_STMT or node.kind == CursorKind.DO_STMT:
            for child in node.walk_preorder():
                if child.kind == CursorKind.CALL_EXPR and child.spelling in spellings and child not in result:
                    result.append(child)
    return result
