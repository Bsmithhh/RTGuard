"""Find critical threads: pthread_create targets using SCHED_FIFO/SCHED_RR,
or functions marked with a `// rtguard: critical` comment."""
from clang.cindex import CursorKind



def find_critical(tu):
    """Return the function cursors that run as critical threads."""
    critical = []
    rt_attrs = set()
    with open(tu.spelling, "r", encoding="utf-8") as f:
        src = f.read()
    lines = src.splitlines(keepends=True)
    for node in tu.cursor.walk_preorder():
        if node.kind == CursorKind.FUNCTION_DECL and node.is_definition() and node.location.file.name == tu.spelling:
            line = node.extent.start.line
            above = lines[line - 2].strip() if line > 1 else ""
            if "rtguard: critical" in above:
                critical.append(node)
        if node.kind == CursorKind.CALL_EXPR and node.spelling == "pthread_attr_setschedpolicy" and node.location.file.name == tu.spelling:
            args = list(node.get_arguments())
            e = args[1].extent
            if src[e.start.offset:e.end.offset] in ("SCHED_FIFO", "SCHED_RR"):
                attr = first_ref(args[0])
                if attr:
                    rt_attrs.add(attr)
    for node in tu.cursor.walk_preorder():
        if node.kind == CursorKind.CALL_EXPR and node.spelling == "pthread_create" and node.location.file.name == tu.spelling:
            args = list(node.get_arguments())
            attr = first_ref(args[1])
            func = first_ref(args[2])
            if func is not None and func.is_definition() and func not in critical and attr in rt_attrs:
                critical.append(func)
    return critical

def first_ref(cursor):
    """Return what the first DECL_REF_EXPR inside cursor refers to, or None."""
    for node in cursor.walk_preorder():
        if node.kind == CursorKind.DECL_REF_EXPR:
            return node.referenced
    return None

def find_ignored_policies(tu):
    """Return the pthread_attr_setschedpolicy calls that are ignored."""
    ignored = []
    policy_calls = []
    explicit_attrs = set()
    with open(tu.spelling, "r", encoding="utf-8") as f:
        src = f.read()
    for node in tu.cursor.walk_preorder():
        if node.kind == CursorKind.CALL_EXPR and node.spelling == "pthread_attr_setschedpolicy" and node.location.file.name == tu.spelling:
            args = list(node.get_arguments())
            e = args[1].extent
            if src[e.start.offset:e.end.offset] in ("SCHED_FIFO", "SCHED_RR"):
                policy_calls.append(node)
        if node.kind == CursorKind.CALL_EXPR and node.spelling == "pthread_attr_setinheritsched" and node.location.file.name == tu.spelling:
            args = list(node.get_arguments())
            e = args[1].extent
            if src[e.start.offset:e.end.offset] == "PTHREAD_EXPLICIT_SCHED":
                attr = first_ref(args[0])
                if attr:
                    explicit_attrs.add(attr)
    for call in policy_calls:
        args = list(call.get_arguments())
        attr = first_ref(args[0])
        if attr not in explicit_attrs:
            ignored.append(call)
    return ignored