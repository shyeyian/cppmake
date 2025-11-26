from cppmakelib import *

def main():
    Package("std").build()
    getattr(Package("main").cppmake, config.target)()