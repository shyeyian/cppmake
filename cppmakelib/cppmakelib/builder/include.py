from cppmakelib.file.file_system  import create_dir, remove_dir, copy_file, copy_dir
from cppmakelib.utility.decorator import syncable

def include(package, file, dir, relpath="."): ...



def include(package, file=None, dir=None, relpath="."):
    try:
        create_dir(f"{package.include_dir}/{relpath}")
        if file is not None and dir is None:
            copy_file(f"{package.git_dir}/{file}", f"{package.include_dir}/{relpath}/{file}")
        elif file is None and dir is not None:
            copy_dir (f"{package.git_dir}/{dir}",  f"{package.include_dir}/{relpath}/")
        else:
            assert False
    except:
        remove_dir(package.install_dir)
        raise

