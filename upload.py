import pathlib
import re
import shutil
import subprocess
import sys

# Dependencies
try:
    import build
except ImportError:
    subprocess.run(
        args=[sys.executable, '-m' ,'pip', 'install', 'build'], 
        check=True
    )
try:
    import twine
except ImportError:
    subprocess.run(
        args=[sys.executable, '-m', 'pip', 'install', 'twine'], 
        check=True
    )

# Git pull
subprocess.run(['git', 'pull'])

# Update subprojects
for project in ['cppmakelib', 'cppmake', 'cppmaked']:
    # Increment version
    with open(pathlib.Path()/project/'pyproject.toml', 'r') as reader:
        pyproject = reader.read()
    pyproject = re.sub(r'^version = "(\d+)\.(\d+)\.(\d+)"$', lambda match: f'version = "{match.group(1)}.{match.group(2)}.{int(match.group(3)) + 1}"', pyproject, flags=re.MULTILINE)
    with open(pathlib.Path()/project/'pyproject.toml', 'w') as writer:
        writer.write(pyproject)

    # Twine upload
    try:
        subprocess.run(
            args=[sys.executable, '-m', 'build'], 
            cwd=project, 
            check=True
        ),
        subprocess.run(
            args=[
                sys.executable, '-m', 
                'twine', 'upload', 'dist/*', 
                '--username', '__token__', 
                '--password', open('pypi-token.txt').read()
            ], 
            cwd=project, 
            check=True
        )
    finally:
        shutil.rmtree(pathlib.Path()/project/'dist')
        shutil.rmtree(pathlib.Path()/project/f'{project}.egg-info')

# Git push
subprocess.run(['git', 'add', '.'])
subprocess.run(['git', 'commit', '-m', 'update'])
subprocess.run(['git', 'push'])
