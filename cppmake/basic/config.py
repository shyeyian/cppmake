from cppmake.system.all import system
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--compiler",                                       default=system.compiler_path   )
parser.add_argument("--std",      choices=["c++20", "c++23", "c++26"],  default="c++26"                )
parser.add_argument("--type",     choices=["debug", "release", "size"], default="debug"                )
parser.add_argument("--parallel", type   =lambda n: int(n),             default=os.process_cpu_count() )
parser.add_argument("--verbose",  action ="store_true",                 default=False                  )
config = parser.parse_args()
config.defines = {}