import json
from multiprocessing import Pool
from datetime import datetime
from dotenv import load_dotenv
import os
import subprocess

def run_command(command: str, message: str):
    result=subprocess.run(command.split(" "), capture_output=True)
    if result.returncode != 0:
        subprocess.run(["docker", "compose", "down"])
        raise RuntimeError(message)
    
load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output/dataset")
VERSION_NAME=os.getenv("VERSION_NAME", datetime.today().strftime("%Y-%m"))

ALGORITHMS=json.loads(os.getenv("ALGORITHMS", "[]"))
SIZES=json.loads(os.getenv("SIZES", "[]"))
BACKENDS=json.loads(os.getenv("BACKENDS", "[]"))
SHOTS=int(os.getenv("SHOTS", 20000))
N_CORES=int(os.getenv("N_CORES"))
JOBS=int(os.getenv("JOBS", os.cpu_count()))

versions=[]
try:
    meta=open(f"{OUTPUT_DIR}/versions.json", "r")
    versions=json.load(meta)
    meta.close()
    if VERSION_NAME in versions:
        raise RuntimeError("Version name already used")
except FileNotFoundError:
    print("No older versions")

run_command("docker compose up -d", "Docker isn't running")

def run_task(algorithm, size, backend):
    from experiment import ex
    ex.run(config_updates={"circuit": algorithm, "size":size, "backend":backend, "shots":SHOTS, "n_cores":N_CORES})
    
inputs=[]
for algorithm in ALGORITHMS:
    for size in SIZES:
        for backend in BACKENDS:
            inputs.append((algorithm, size, backend))
            
start_time=datetime.now().time().strftime("%H:%M:%S")
with Pool(processes=JOBS) as pool:
    pool.starmap(run_task, inputs)
end_time=datetime.now().time().strftime("%H:%M:%S")

from create_dataset import process_all_completed
metadata=process_all_completed()

metadata["shots"]=SHOTS
metadata["start_time"]=start_time
metadata["end_time"]=end_time
metadata["date"]=datetime.today().strftime("%Y-%m-%d")
with open(f"{OUTPUT_DIR}/{VERSION_NAME}/metadata.json", "w") as meta:
    json.dump(metadata, meta, indent=2)

with open(f"{OUTPUT_DIR}/versions.json", "w") as meta:
    versions.append(VERSION_NAME)
    json.dump(versions, meta)

run_command(f"git add {OUTPUT_DIR}", "Error in git add")
run_command(f"git commit -m {VERSION_NAME}", "Error during git commit")
run_command("git push --force", "Error in git push")

subprocess.run(["docker", "compose", "down"], check=True)