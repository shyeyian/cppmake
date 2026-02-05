def red(string: str) -> str:
    return f'\033[31m{string}\033[39m'

def green(string: str) -> str:
    return f'\033[32m{string}\033[39m'

def yellow(string: str) -> str:
    return f'\033[33m{string}\033[39m'

def blue(string: str) -> str:
    return f'\033[34m{string}\033[39m'

def bold(string: str) -> str:
    return f'\033[1m{string}\033[22m'