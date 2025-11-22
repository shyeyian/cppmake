from cppmakelib import *

def main():
    Package("std").cppmake.package()
    getattr(main_package.cppmake, config.target)()