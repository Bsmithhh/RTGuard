"""Walk calls reachable from a function, following functions defined in the TU."""
from clang.cindex import CursorKind


def reachable_calls(func):
    """Return the CALL_EXPR cursors reachable from func."""
    reached = []
    for node in func.walk_preorder():
        if node.kind == CursorKind.CALL_EXPR:
            reached.append(node)
    return reached
