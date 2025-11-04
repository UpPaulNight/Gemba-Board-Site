import sys


__SHOULD_IGNORE_DEBUG = False

def parse_args() -> None:
    global __SHOULD_IGNORE_DEBUG
    
    args = sys.argv

    __SHOULD_IGNORE_DEBUG = len(args) > 1 and args[1] == 'false'

def should_show_debug() -> bool:
    return not __SHOULD_IGNORE_DEBUG
