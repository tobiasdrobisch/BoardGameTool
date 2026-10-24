# Debug utility for printing messages with the source filename and line number.

# Import this in the file you want to debug:
# from debug_utils import debug
# If debug_utils.py is in a package, use its package path, e.g.:
# from app.debug_utils import debug
#
# Usage:
# debug("User logged in") -> in auth.py
# debug("Number of games:", len(games)) -> in games.py
#
# Output example:
# [auth.py:15] User logged in
# [games.py:42] Number of games: 5


import inspect
import os


def debug(*args):
    frame = inspect.currentframe().f_back
    print(
        f"[{os.path.basename(frame.f_code.co_filename)}:"
        f"{frame.f_lineno}]",
        *args
    )