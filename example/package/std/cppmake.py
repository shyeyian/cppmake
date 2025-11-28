from cppmakelib import *

if type(compiler) == Clang or type(compiler) == Emcc:
    package.compile_flags += [
        "-Wno-include-angled-in-module-purview",
        "-Wno-reserved-module-identifier"
    ]
        
def build():
    std_module = compiler.std_module()
    create_dir(package.include_dir)
    copy_dir(parent_path(std_module), package.include_dir)
    with open(std_module, 'r') as reader:
        content = reader.read().split("export module std;")
    with open(f"{package.include_dir}/include", 'w') as writer:
        writer.write(content[0].replace("module;", ""))
    with open(f"{package.include_dir}/export", 'w') as writer:
        writer.write(content[1])
