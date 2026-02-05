import shutil
import subprocess
import sys

# Install package
try:
    subprocess.run(args=[sys.executable, '-m', 'build'],               check=True)
    subprocess.run(args=[sys.executable, '-m', 'pip', 'install', '-e', '.'], check=True)
finally:
    shutil.rmtree('build',            ignore_errors=True)
    shutil.rmtree('dist' ,            ignore_errors=True)
    shutil.rmtree('cppmake.egg-info', ignore_errors=True)