"""Load rules.yaml and match calls against it."""
import yaml


def load(path):
    """Return the list of rules in path."""
    with open(path, "r", encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    return rules


def match(call, rules):
    """Return the rule that call violates, or None."""
    for rule in rules:
        if call.spelling in rule["functions"]:
            return rule
    return None
