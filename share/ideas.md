0. 每个package应该独立build。不管子package的header, 也不管子package的module。
   include header和import module **只解析同package下的依赖关系**
    ***module.belong_package一定是context.package***   

 


1. `module.__init__()`依赖`package.build()`, 这样`compiler.preprocess_file()`就能正常工作了。
 - 分布式编译始终需要`compiler.preprocess_file()`。

2. 加入"--machine=x84_64-pc-linux-gnu"选项，或 
    - "--machine-architecture=xxx",
    - "--machine-vendor=xxx",
    - "--machine-system=xxx
    - "--machine-abi=xxx",
    注意"--target=xxx"已经被占用为"编译目标"了。

    - 用"--architecture"。

3. **cppmaked**不现实