import sys
import os
from dotenv import load_dotenv
import json
import shutil
import subprocess

versions=sys.argv
versions.pop(0)
if len(versions) == 0:
    raise RuntimeError("No parameters")

load_dotenv()
OUTPUT_DIR=os.getenv("OUTPUT_DIR", "../dataset")

try:
    file=open(f"{OUTPUT_DIR}/versions.json", "r")
    all_versions=json.load(file)
    file.close()
    for version in versions:
        if version not in all_versions:
            raise RuntimeError(f"{version} version doesn't exist")
except FileNotFoundError:
    raise FileNotFoundError("No versions avaible")

for version in versions:
    shutil.rmtree(f"{OUTPUT_DIR}/{version}")
    all_versions.remove(version)

with open(f"{OUTPUT_DIR}/versions.json", "w") as file:
    json.dump(all_versions, file)

if len(all_versions) == 0:
    shutil.rmtree(OUTPUT_DIR)

subprocess.run(["git", "add", OUTPUT_DIR], check=True)
subprocess.run(["git", "commit", "-m", f"Removed version(s): {", ".join(versions)}"], check=True)
subprocess.run(["git", "push", "--force"], check=True)