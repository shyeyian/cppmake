from cppmakelib import *

def main():
    if Package("main").cppmake is not None:
        getattr(Package("main").cppmake, config.target)()
    else: # default
        Source("main").compile()