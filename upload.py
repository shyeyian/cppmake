import re
import shutil
import subprocess

# Git pull
subprocess.run(f"git pull", shell=True, check=False)

# Update subprojects
for project in ["cppmakelib", "cppmake"]:
    # Increment version
    with open(f"{project}/pyproject.toml", 'r') as reader:
        pyproject = reader.read()
    pyproject = re.sub(r'^version = "(\d+)\.(\d+)\.(\d+)"$', lambda match: f'version = "{match.group(1)}.{match.group(2)}.{int(match.group(3)) + 1}"', pyproject, flags=re.MULTILINE)
    with open(f"{project}/pyproject.toml", 'w') as writer:
        writer.write(pyproject)

    # Twine upload
    try:
        subprocess.run(f"python -m build",                                                                     shell=True, cwd=project, check=True)
        subprocess.run(f"twine upload dist/* --username __token__ --password {open("pypi-token.txt").read()}", shell=True, cwd=project, check=True)
    finally:
        shutil.rmtree(f"{project}/dist")
        shutil.rmtree(f"{project}/{project}.egg-info")

# Git push
subprocess.run(f"git add .",            shell=True, check=False)
subprocess.run(f"git commit -m update", shell=True, check=False)
subprocess.run(f"git push",             shell=True, check=False)
