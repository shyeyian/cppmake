from cppmakelib import *

def main():
    if not exist_dir("package/std"): # install std as default
        create_dir  ("package/std/module")
        open        ("package/std/module/std.cpp", 'w').write(default_std_module)
        open        ("package/std/cppmake.py",     'w').write(default_std_cppmake)
    Package("std").build()

    if Package("main").cppmake is not None:
        getattr(Package("main").cppmake, config.target)()
    else: # compile Source("main") as default
        Source("main").compile()




default_std_module = \
"""
module;
#include <include>

export module std;
#include <export>
"""

default_std_cppmake = \
"""
from cppmakelib import *

if type(compiler) == Clang or type(compiler) == Emcc:
    self.compile_flags += [
        "-Wno-include-angled-in-module-purview",
        "-Wno-reserved-module-identifier"
    ]
        
def build():
    std_module = compiler.std_module()
    create_dir(self.include_dir)
    copy_dir(parent_path(std_module), self.include_dir)
    with open(std_module, 'r') as reader:
        content = reader.read().split("export module std;")
    with open(f"{self.include_dir}/include", 'w') as writer:
        writer.write(content[0].replace("module;", ""))
    with open(f"{self.include_dir}/export", 'w') as writer:
        writer.write(content[1])
"""