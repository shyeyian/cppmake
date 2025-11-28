from cppmakelib import *

def make():
    Source("main").compile()

def run():
    Executable("main").execute()

def test():
    for file in iterate_dir("source/test"):
        Source(file=file).compile()