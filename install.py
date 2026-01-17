import pathlib
import shutil
import subprocess
import sys

# Install package
for project in ['cppmakelib', 'cppmake', 'cppmaked']:
    try:
        subprocess.run(args=[sys.executable, '-m', 'build'],               cwd=project, check=True)
        subprocess.run(args=[sys.executable, '-m', 'pip', 'install', '.'], cwd=project, check=True)
    finally:
        shutil.rmtree(pathlib.Path()/project/'build',               ignore_errors=True)
        shutil.rmtree(pathlib.Path()/project/'dist' ,               ignore_errors=True)
        shutil.rmtree(pathlib.Path()/project/f'{project}.egg-info', ignore_errors=True)