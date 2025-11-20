from cppmake.basic.config import config
import importlib

def import_file(file): ...



def import_file(file, to_config=False):
    if file is not None:
        module = importlib.machinery.SourceFileLoader(
            fullname=file.removesuffix(".py").replace('/', '.'), 
            path=file
        ).load_module()
    else:
        module = _EmptyModule()
    if not hasattr(module, "build"):
           setattr(module, "build", lambda: None)
    if not hasattr(module, "defines"):
           setattr(module, "defines", {})
    if to_config:
        config.defines = module.defines
    return module


class _EmptyModule:
    pass
