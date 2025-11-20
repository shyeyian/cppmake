from cppmake.file.file_system  import create_dir, remove_dir, copy_dir
from cppmake.utility.decorator import syncable

@syncable
async def async_include(package, dir, relpath="."):
    try:
        create_dir(package.include_dir)
        copy_dir(f"{package.git_dir}/{dir}", f"{package.include_dir}" if relpath == "." else f"{package.include_dir}/{relpath.split('/')[0]}")
    except:
        remove_dir(package.install_dir)
        raise

