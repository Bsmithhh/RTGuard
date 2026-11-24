import sys, os
from clang.cindex import Index, CursorKind

QNX_INC = os.path.expanduser("~/qnx800/target/qnx/usr/include")
tu = Index.create().parse(
    sys.argv[1],
    args=["-nostdinc", f"-I{QNX_INC}", "-D__QNXNTO__", "-D__aarch64__",
          "-D__LITTLEENDIAN__", "-Wno-pragma-pack"],
)

for d in tu.diagnostics:
    print("clang:", d)

for node in tu.cursor.walk_preorder():
    if node.kind == CursorKind.CALL_EXPR and node.location.file \
       and node.location.file.name == sys.argv[1]:
        print(f"{node.location.file}:{node.location.line}  {node.spelling}")