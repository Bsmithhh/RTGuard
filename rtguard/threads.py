"""Find critical threads: pthread_create targets using SCHED_FIFO/SCHED_RR,
or functions marked with a `// rtguard: critical` comment."""
from clang.cindex import CursorKind



def find_critical(tu):
    """Return the function cursors that run as critical threads."""
    critical = []
    with open(tu.spelling, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for node in tu.cursor.walk_preorder():
        if node.kind == CursorKind.FUNCTION_DECL and node.is_definition() and node.location.file.name == tu.spelling:
            line = node.extent.start.line
            above = lines[line - 2].strip() if line > 1 else ""
            if "rtguard: critical" in above:
                critical.append(node)
    return critical

