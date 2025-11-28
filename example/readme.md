This is an example of C++20 modules make system.
- ```sh
  cppmake .
  ```
  The output executable will be at `binary/debug/source/main`.

- ```sh
  cppmake . --type=release
  ```
  The output executable will be at `binary/release/source/main` in release mode.

- ```sh
  cppmake . --compiler=/usr/bin/clang++ --verbose
  ```
  Will choose `clang++` as the C++ compiler.

  For more information, run
  ```sh
  cppmake --help
  ```
  