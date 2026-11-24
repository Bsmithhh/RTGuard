"""Parse C/C++ files with libclang against the QNX 8.0 headers."""
import os
from clang.cindex import Index

QNX_INC = os.path.expanduser("~/qnx800/target/qnx/usr/include")
QNX_ARGS = ["-nostdinc", f"-I{QNX_INC}", "-D__QNXNTO__", "-D__aarch64__",
            "-D__LITTLEENDIAN__", "-Wno-pragma-pack"]


def parse(path, extra_args=()):
    """Return a libclang TranslationUnit for path."""
    return Index.create().parse(path, args=QNX_ARGS + list(extra_args))
