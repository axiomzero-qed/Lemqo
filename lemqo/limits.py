"""Fixed v1 acceptance limits, shared by byte parsing and the kernel.

These bounds can reject valid derivations. They do not add inference rules.
"""

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_JSON_DEPTH = 96
MAX_JSON_VALUES = 200_000
MAX_STRING_LENGTH = 128
MAX_INTEGER_DIGITS = 9
MAX_FORMULAS = 10_000
MAX_FORMULA_DEPTH = 64
MAX_CLAIM_NODES = 10_000
MAX_STEPS = 20_000
MAX_PREMISES = 256
MAX_CONTEXT = 256
MAX_CONTEXT_MEMBERSHIPS = 200_000
