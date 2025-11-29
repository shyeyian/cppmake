# Cppmake: A C++20 Modules Build System

Cppmake is a modern, fast, and accurate C++ build system focusing on C++20 Modules.

Cppmake aims to
- Make everything modular.
- Easily modularize third-party libraries.
- Be fast, parallel, and fully cached.

Cppmake is written in pure Python with no additional pip dependencies.

# Install

Use pip to install cppmake:
```sh
pip install cppmake
```
Or install from source:
```sh
git clone https://github.com/anonymouspc/cppmake
cd cppmake
python install.py
```

# Getting Started

In a cppmake project: 
- module `aaa.bbb` should be placed at `module/aaa/bbb.cpp`
- module `aaa:ccc` should be placed at `module/aaa/ccc.cpp`
- source `main` should be placed at `source/main.cpp`
- `std` module will be auto-installed.

For example:
```
├── module
│   ├── aaa.cpp
│   ├── aaa
│   │   ├── bbb.cpp // aaa.bbb
│   │   └── ccc.cpp // aaa:ccc
│   └── ddd.cpp
├── source
│   └── main.cpp
└── cppmake.py
```
Then, run
```sh
cppmake
```
The output will be generated in the binary directory.

# Advanced

Cppmake provides various configurable options, such as:
```sh
cppmake --compiler=clang++ --std=c++23
```
```sh
cppmake --compiler=/opt/gcc/bin/g++ --linker=lld --std=c++26 --type=release --target=make --parallel=$(nproc)
```

System/compiler support:
|         | clang | emcc | gcc | msvc |
|:-------:|:-----:|:----:|:---:|:----:| 
| Linux   | ✓     | ✓    | ✓   | N/A  |  
| Macos   | ✓     | ✓    | ✓   | N/A  |  
| Windows | ✗     | ✗    | ✗   | ✗    | 
- ✓: Supported and tested.
- ✗: Not implemented yet; planned for future releases.
- *(The author does not own a Windows PC. Contributions for Windows supportare welcome!)*

# Configure

Cppmake uses a `cppmake.py` file (pure Python) to describe the C++ project. The configuration is entirely standard Python syntax.

For example:
```py
from cppmakelib import *
def make():
    Source("main").compile()
```
This `cppmake.py` defines a single source `source/main.cpp`, which will be
built into a binary.
- *(Imported modules and packages are built automatically before compiling the source. For example, if `source/main.cpp` imports module my_module and module `boost.asio`, then Cppmake will precompile module `my_module`, cmake build `boost`, and precompile module `boost.asio` before finally compiling `source/main.cpp`.)*
- *(By default, the imported modules and packages form a [directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph) and are executed with maximum possible parallelism, depending on your cpu thread count. You can control the level of parallelism using `cppmake --parallel=N`, or force serial compilation through `cppmake --parallel=1`.)*

Another example:
```py
from cppmakelib import *

if type(compiler) == Gcc:
    compiler.compile_flags += ["-fno-inline"] # global
    compiler.define_macros |= {"NDEBUG": '1'} # global

package.define_macros = {"MY_MACRO": "42"} # package-local

def build(): # select a source file to compile
    if type(system) == Linux:
        Source("linux").compile()

def test(): # compile and test all units
    for file in iterate_dir("source/test", recursive=True):
        Source(file=file).compile()
        Executable(file=file).run()
```
This `cppmake.py` defines 2 targets (switchable via
`cppmake --target=build|test`) and several configuration rules. You can
easily extend it with any other Python code.

# Integrating third-party packages

Third-party packages should be located `package/`, for example
```
├── module
│   ├── aaa.cpp
│   ├── aaa
│   │   ├── bbb.cpp // aaa.bbb
│   │   └── ccc.cpp // aaa:ccc
│   └── ddd.cpp
├── source
│   └── main.cpp
├── package
│   ├── boost
│   │   ├── git
│   │   │   └── [git clone]
│   │   ├── module
│   │   │   ├── boost.cpp // boost
│   │   │   └── boost
│   │   │       ├── asio.cpp // boost.asio
│   │   │       ├── beast.cpp // boost.beast
│   │   │       └── numeric.cpp // boost.numeric
│   │   │           ├── interval.cpp // boost.numeric.interval
│   │   │           └── ublas.cpp // boost.numeric.ublas
│   │   └── cppmake.py
│   └── eigen
│       ├── git
│       │   └── [git clone]
│       ├── module
│       │   └── eigen.cpp // eigen
│       └── cppmake.py
└── cppmake.py
```

In `package/boost/cppmake.py` we can define a `build()` function to describe how it should be built. For example:
```py
# package/boost/cppmake.py
from cppmakelib import *

def build():
    cmake.build(
        package=package,
        args=[
            "-DBUILD_SHARED_LIBS=OFF"
        ]
    )
```
Then:
```cpp
// package/boost/module/boost/asio.cpp
module;
#include <boost/asio.hpp>
export module boost.asio;
export namespace boost::asio
{
    using boost::asio::io_context;
    //...
}
```
will modularize boost.asio into a module.

Builder support: 
| cmake | include* | makefile | msbuild |
|:-----:|:--------:|:--------:|:-------:| 
| ✓     | ✓        | ✓        | ✗       |
- ✓: Supported and tested.
- ✗: Not implemented yet; planned for future releases.
- *(include: means header-only libraries.)*

# Thank you!
