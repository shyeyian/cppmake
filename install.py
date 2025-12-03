import shutil
import subprocess

for project in ["cppmakelib", "cppmake"]:
    subprocess.run(f"python -m build", shell=True, cwd=project, check=True)
    subprocess.run(f"pip install .",   shell=True, cwd=project, check=True)
    shutil.rmtree(f"{project}/build")
    shutil.rmtree(f"{project}/dist")
    shutil.rmtree(f"{project}/{project}.egg-info")