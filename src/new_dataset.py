import json
from datetime import datetime
from dotenv import load_dotenv
import os
import subprocess
import platform
import psutil

class QSimBenchError(Exception):
    pass

load_dotenv()

OUTPUT_DIR=os.getenv("OUTPUT_DIR", "../dataset")
VERSION_NAME=os.getenv("VERSION_NAME", datetime.today().strftime("%Y-%m"))

ALGORITHMS=json.loads(os.getenv("ALGORITHMS"))
SIZES=json.loads(os.getenv("SIZES"))
BACKENDS=json.loads(os.getenv("BACKENDS"))
SHOTS=os.getenv("SHOTS", 20000)
N_CORES= os.getenv("N_CORES") if os.getenv("N_CORES") != "all" else None
if not ALGORITHMS or not SIZES or not BACKENDS:
    raise QSimBenchError("Empty run parameter(s)")

JOBS=os.getenv("JOBS", os.cpu_count())
LOAD=os.getenv("LOAD", os.cpu_count())
MEMFREE=os.getenv("MEMFREE")
MEMSUSPEND=os.getenv("MEMSUSPEND")
DELAY=os.getenv("DELAY", "0")

if not MEMFREE or not MEMSUSPEND:
    raise QSimBenchError("Missing parallel parameter(s)")

try:
    meta=open(f"{OUTPUT_DIR}/versions.json", "r")
    versions=json.load(meta)
    meta.close()
    if VERSION_NAME in versions:
        raise QSimBenchError("Version name already used")
except FileNotFoundError:
    versions=[]

try:
    os.remove("times.csv")
except:
    pass

try:
    os.remove("errors.txt")
except:
    pass

command=["parallel", "--progress", "--jobs", JOBS, "--load", LOAD, "--memfree", MEMFREE, "--memsuspend", MEMSUSPEND, "--delay", DELAY, f"python experiment.py with circuit={{1}} size={{2}} backend={{3}} shots={SHOTS} n_cores={N_CORES}", ":::", *ALGORITHMS, ":::", *map(str, SIZES), ":::", *BACKENDS]
start_time=datetime.now().strftime("%H:%M:%S, %Y-%m-%d")
subprocess.run(command)
end_time=datetime.now().strftime("%H:%M:%S, %Y-%m-%d")

from create_dataset import process_all_completed
process_all_completed()

metadata={"version": VERSION_NAME}
ALGORITHMS.sort()
metadata["algorithms"]=ALGORITHMS
SIZES.sort()
metadata["sizes"]=SIZES
BACKENDS.sort()
metadata["backends"]=BACKENDS

metadata["shots"]=SHOTS
metadata["start_time"]=start_time
metadata["end_time"]=end_time

metadata["os"]=platform.system()
metadata["os_version"]=platform.version()
metadata["os_release"]=platform.release()
metadata["architecture"]=platform.machine()
metadata["python_version"]=platform.python_version()

metadata["cpu_name"] = platform.processor() or "Unknown"
metadata["cpu_cores_physical"] = psutil.cpu_count(logical=False)
metadata["cpu_cores_logical"] = psutil.cpu_count(logical=True)
metadata["cpu_freq_mhz"] = psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {}

vm = psutil.virtual_memory()
metadata["memory_total_GB"] = round(vm.total / (1024**3), 2)
metadata["memory_available_GB"] = round(vm.available / (1024**3), 2)

libraries=subprocess.getoutput("uv pip freeze").splitlines()
libraries.pop(0)
metadata["libraries"]=libraries

print("Metadata created")

with open(f"{OUTPUT_DIR}/{VERSION_NAME}/metadata.json", "w") as meta:
    json.dump(metadata, meta, indent=2)
print("Metadata saved")

with open(f"{OUTPUT_DIR}/versions.json", "w") as vers:
    versions.append(VERSION_NAME)
    json.dump(versions, vers)
print("Versions file updated")

try:
    subprocess.run(["git", "add", f"{OUTPUT_DIR}/{VERSION_NAME}", f"{OUTPUT_DIR}/versions.json"], check=True, stdout=subprocess.PIPE)
    print("git add done")
except:
    print("git add failed")

try:
    subprocess.run(["git", "commit", "-m", f"Added version {VERSION_NAME}"], check=True, stdout=subprocess.PIPE)
    print("git commit done")
except:
    print("git commit failed")

try:
    subprocess.run(["git", "push", "--force"], check=True, stdout=subprocess.PIPE)
    print("git push done")
except:
    print("git push failed")
