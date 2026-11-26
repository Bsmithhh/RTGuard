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
