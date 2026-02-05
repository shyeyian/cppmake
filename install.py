import pathlib
import shutil
import subprocess
import sys

# Install package
try:
    subprocess.run(args=[sys.executable, '-m', 'build'],               check=True)
    subprocess.run(args=[sys.executable, '-m', 'pip', 'install', '.'], check=True)
finally:
    shutil.rmtree('build',                                 ignore_errors=True)
    shutil.rmtree('dist' ,                                 ignore_errors=True)
    shutil.rmtree(pathlib.Path()/'src'/'cppmake.egg-info', ignore_errors=True)