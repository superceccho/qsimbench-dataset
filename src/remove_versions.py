import sys
import os
from dotenv import load_dotenv
import json
import shutil
import subprocess

class QSimBenchError(Exception):
    pass

versions=sys.argv
versions.pop(0)
if len(versions) == 0:
    raise QSimBenchError("No parameters")

load_dotenv()
OUTPUT_DIR=os.getenv("OUTPUT_DIR", "../dataset")

vers_path = f"{OUTPUT_DIR}/versions.json"
if os.path.exists(vers_path):
    with open(vers_path, "r") as file:
        all_versions = json.load(file)

    if not all_versions:
        raise QSimBenchError("No versions")
    
    for version in versions:
        if version not in all_versions:
            raise QSimBenchError(f"{version} version doesn't exist")
else:
    raise QSimBenchError("No versions file")

removed = []
for version in versions:
    try:
        shutil.rmtree(f"{OUTPUT_DIR}/{version}")
    except:
        pass
    all_versions.remove(version)
    removed.append(f"{OUTPUT_DIR}/{version}")
    print(f"version {version} deleted")
print("Versions deleted")

with open(f"{OUTPUT_DIR}/versions.json", "w") as file:
    json.dump(all_versions, file)
print("Updated versions file")

try:
    subprocess.run(["git", "add", *removed], check=True, stdout=subprocess.PIPE)
    print("git add done")
except:
    print("git add failed")

try:
    subprocess.run(["git", "commit", "-m", f"Removed version(s): {", ".join(versions)}"], check=True, stdout=subprocess.PIPE)
    print("git commit done")
except:
    print("git commit failed")

try:
    subprocess.run(["git", "push", "--force"], check=True, stdout=subprocess.PIPE)
    print("git push done")
except:
    print("git push failed")