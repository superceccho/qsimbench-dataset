import json
from multiprocessing import Pool
from datetime import datetime
from dotenv import load_dotenv
import os
from time import sleep

os.system("docker compose up -d")
sleep(5)

load_dotenv()

OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output/dataset")
VERSION_NAME=os.getenv("VERSION_NAME", datetime.today().strftime("%Y-%m"))

ALGORITHMS=json.loads(os.getenv("ALGORITHMS", "[]"))
SIZES=json.loads(os.getenv("SIZES", "[]"))
BACKENDS=json.loads(os.getenv("BACKENDS", "[]"))
SHOTS=int(os.getenv("SHOTS", 20000))
N_CORES=int(os.getenv("N_CORES"))
JOBS=int(os.getenv("JOBS", os.cpu_count()))

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

from create_dataset import process_all_completed
metadata=process_all_completed()
end_time=datetime.now().time().strftime("%H:%M:%S")

metadata["shots"]=SHOTS
metadata["start_time"]=start_time
metadata["end_time"]=end_time
metadata["date"]=datetime.today().strftime("%Y-%m-%d")
with open(f"{OUTPUT_DIR}/{VERSION_NAME}/metadata.json", "w") as meta:
    json.dump(metadata, meta, indent=2)

try:
    meta=open(f"{OUTPUT_DIR}/metadata.json", "r+")
    versions=json.load(meta)
    if VERSION_NAME not in versions:
        versions.append(VERSION_NAME)
    meta.seek(0)
    json.dump(versions, meta)
    meta.close()
except FileNotFoundError:
    versions=[VERSION_NAME]
    meta=open(f"{OUTPUT_DIR}/metadata.json", "w")
    json.dump(versions, meta)
    meta.close()

os.system("docker compose down")
sleep(5)