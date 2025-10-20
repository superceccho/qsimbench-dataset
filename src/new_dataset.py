import json
from datetime import datetime
from dotenv import load_dotenv
import os
import subprocess
import platform
import psutil
import atexit

def close_compose():
    subprocess.run("docker compose down", shell=True)
    
load_dotenv()

OUTPUT_DIR=os.getenv("OUTPUT_DIR", "../dataset")
VERSION_NAME=os.getenv("VERSION_NAME", datetime.today().strftime("%Y-%m"))

ALGORITHMS=json.loads(os.getenv("ALGORITHMS"))
SIZES=json.loads(os.getenv("SIZES"))
BACKENDS=json.loads(os.getenv("BACKENDS"))
SHOTS=os.getenv("SHOTS", 20000)
N_CORES=os.getenv("N_CORES")
if not ALGORITHMS or not SIZES or not BACKENDS:
    raise RuntimeError("Empty run parameter(s)")

JOBS=os.getenv("JOBS", os.cpu_count())
LOAD=os.getenv("LOAD", os.cpu_count())
MEMFREE=os.getenv("MEMFREE")
MEMSUSPEND=os.getenv("MEMSUSPEND")
DELAY=os.getenv("DELAY", "0")

if not MEMFREE or not MEMSUSPEND:
    raise RuntimeError("Missing parallel parameter(s)")

try:
    meta=open(f"{OUTPUT_DIR}/versions.json", "r")
    versions=json.load(meta)
    meta.close()
    if VERSION_NAME in versions:
        raise RuntimeError("Version name already used")
except FileNotFoundError:
    versions=[]

subprocess.run(["docker", "compose", "up", "-d"], check=True)
print("Docker containers running")

atexit.register(close_compose)

command=["parallel", "--jobs", JOBS, "--load", LOAD, "--memfree", MEMFREE, "--memsuspend", MEMSUSPEND, "--delay", DELAY, "--progress", f"python experiment.py with circuit={{1}} size={{2}} backend={{3}} shots={SHOTS} n_cores={N_CORES}", ":::", *ALGORITHMS, ":::", *map(str, SIZES), ":::", *BACKENDS]
start_time=datetime.now().time().strftime("%H:%M:%S")
subprocess.run(command, check=True)
end_time=datetime.now().time().strftime("%H:%M:%S")

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
metadata["date"]=datetime.today().strftime("%Y-%m-%d")

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

libraries=subprocess.getoutput("pip freeze").splitlines()
metadata["libraries"]=libraries

with open(f"{OUTPUT_DIR}/{VERSION_NAME}/metadata.json", "w") as meta:
    json.dump(metadata, meta, indent=2)

with open(f"{OUTPUT_DIR}/versions.json", "w") as vers:
    versions.append(VERSION_NAME)
    json.dump(versions, vers)

subprocess.run(["git", "add", OUTPUT_DIR], check=True)
subprocess.run(["git", "commit", "-m", f"Added version {VERSION_NAME}"], check=True)
subprocess.run(["git", "push", "--force"], check=True)