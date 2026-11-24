"""Print compiler-style warnings."""


def warn(call, rule):
      """Print `file:line: warning: [RULE] message` followed by the fix."""
      loc = call.location
      print(f"{loc.file.name}:{loc.line}:{loc.column}: warning: "
            f"[{rule['id']}] {call.spelling} {rule['message']}")
      print(f"  fix: {rule['fix']}")
    
