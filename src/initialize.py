import subprocess
import os

env_path = ".env"

if not os.path.exists(env_path):
    with open(env_path, "w") as file:
        file.write("MONGO_INITDB_ROOT_USERNAME=qsimbench\n" \
                    "MONGO_INITDB_ROOT_PASSWORD=qsimbench2025\n" \
                    "MONGO_DATABASE=sacred\n" \
                    "VERSION_NAME=\n" \
                    "OUTPUT_DIR=../dataset\n" \
                    "ALGORITHMS=[]\n" \
                    "SIZES=[]\n" \
                    "BACKENDS=[]\n" \
                    "SHOTS=1000\n" \
                    "N_CORES=1\n" \
                    "JOBS=8\n" \
                    "LOAD=6\n" \
                    "MEMFREE=1G\n" \
                    "MEMSUSPEND=0\n" \
                    "DELAY=60\n")

    print(".env file created")

print("Starting docker...")
subprocess.run(["docker", "compose", "up", "-d"])

print("Serializing circuits...")
subprocess.run(["python", "utils/serialise_qc.py"])
print("Circuit serialized")

print("Serializing backends...")
subprocess.run(["python", "utils/serialise_qpu.py"])
print("Backends serialized")