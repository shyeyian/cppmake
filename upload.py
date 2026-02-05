import re
import shutil
import subprocess
import sys

# Pip install
try:
    import build
except ImportError:
    subprocess.run(args=[sys.executable, '-m' ,'pip', 'install', 'build'], check=True)
try:
    import twine
except ImportError:
    subprocess.run(args=[sys.executable, '-m', 'pip', 'install', 'twine'], check=True)

# Git pull
subprocess.run(['git', 'pull'])

# Twine upload
with open('pyproject.toml', 'r') as reader:
    pyproject = reader.read()
pyproject = re.sub(
    pattern=r'^version = "(\d+)\.(\d+)\.(\d+)"$', 
    repl   =lambda match: f'version = "{match.group(1)}.{match.group(2)}.{int(match.group(3)) + 1}"', 
    string =pyproject, 
    flags  =re.MULTILINE
)
with open('pyproject.toml', 'w') as writer:
    writer.write(pyproject)
try:
    subprocess.run(
        args=[sys.executable, '-m', 'build'], 
        check=True
    )
    subprocess.run(
        args=[
            sys.executable, '-m', 
            'twine', 'upload', 'dist/*', 
            '--username', '__token__', 
            '--password', open('pypi-token.txt').read()
        ], 
        check=True
    )
finally:
    shutil.rmtree('dist')
    shutil.rmtree('cppmake.egg-info')

# Git push
subprocess.run(['git', 'add', '.'])
subprocess.run(['git', 'commit', '-m', 'update'])
subprocess.run(['git', 'push'])
