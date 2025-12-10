from pymongo import MongoClient

from mqt.bench import get_benchmark
from qiskit.qasm2 import dumps
import datetime
import mqt.bench as mb

import os
from pymongo import MongoClient

from dotenv import load_dotenv

load_dotenv()

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USER = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')

DB_NAME = 'quantum_circuit'
COLLECTION_NAME = 'mqt.bench==1.1.9'

mongo_url = f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/'

client = MongoClient(mongo_url)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

if __name__ == '__main__':
    algs = ['ae', 'bmw_quark_cardinality', 'bv', 'dj', 'ghz', 'graphstate', 'grover', 'hhl', 'qft', 'qftentangled', 'qnn', 'qpeexact', 'qpeinexact', 'qwalk', 'randomcircuit', 'vqe_real_amp', 'vqe_su2', 'vqe_two_local', 'wstate']
    max_qubits = 15
    print(f"# of combinations: {(max_qubits - 3) * len(algs)}")
    for n in range(4, max_qubits + 1):
        for alg in algs:
            # Get the benchmark for the algorithm and number of qubits
            qc = get_benchmark(benchmark=alg, level=mb.BenchmarkLevel.ALG, circuit_size=n, random_parameters=True)
            #qc_decomposed = qc.decompose(reps=2)
            qc_decomposed = qc.copy()
            
            qasm_str = dumps(qc)
            decomposed_qasm_str = dumps(qc_decomposed)
            
            no_final_measurement = qc_decomposed.remove_final_measurements(inplace=False)
            
            inverse = no_final_measurement.inverse()
            inverse_qasm_str = dumps(inverse)
            no_final_measurement.barrier()
            mirror = no_final_measurement.compose(inverse)
            mirror.measure_all(inplace=True)
            mirror_qasm_str = dumps(mirror)

            
            # Prepare the document to insert into MongoDB
            doc = {
                "_id": f"{alg}_{n}",
                "algorithm": alg,
                "size": n,
                "circuit": qasm_str,
                "inverse": inverse_qasm_str,
                "mirror": mirror_qasm_str,
                #"decomposed": decomposed_qasm_str,
                "created_at": datetime.datetime.now(datetime.timezone.utc),
                "qasm_version": "2.0",
            }
            
            # Insert the document into the MongoDB collection
            try:
                collection.insert_one(doc)
                print(f"Successfully inserted benchmark for {alg} with {n} qubits")
            except Exception as e:
                print(f"Error inserting benchmark for {alg} with {n} qubits: {e}")

    algorithms = {"_id": "algorithms", "algorithms": algs}
    collection.insert_one(algorithms)

    sizes = {"_id": "sizes", "sizes": list(range(4, max_qubits+1))}
    collection.insert_one(sizes)