from pymongo import MongoClient
from qiskit_aer.backends.aer_simulator import AerBackendConfiguration
from qiskit_aer import AerSimulator

import datetime

import os
from pymongo import MongoClient

from dotenv import load_dotenv
from pathlib import Path

from tqdm import tqdm

dotenv_path = Path(__file__).parent.parent.parent / "src" / ".env"
load_dotenv(dotenv_path=dotenv_path)

MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_USER = os.getenv('MONGO_INITDB_ROOT_USERNAME')
MONGO_PASSWORD = os.getenv('MONGO_INITDB_ROOT_PASSWORD')

DB_NAME = 'quantum_backends'
COLLECTION_NAME = 'qiskit_fake_backends'

mongo_url = f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/'

client = MongoClient(mongo_url)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def make_serializable(obj):
    if isinstance(obj, complex):
        return {'__complex__': True, 'real': obj.real, 'imag': obj.imag}
    elif isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(v) for v in obj]
    else:
        return obj
    
def restore_complex(obj):
    if isinstance(obj, dict):
        if '__complex__' in obj:
            return complex(obj['real'], obj['imag'])
        return {k: restore_complex(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [restore_complex(v) for v in obj]
    else:
        return obj

def serialize_backends(backends):
    """
    Serializes a list of FakeBackendV2 instances into MongoDB.

    Args:
        backends (List[BackendV2]): List of FakeBackendV2 or similar backends.
    """
    inserted = []

    for backend in backends:
        name = backend.name if hasattr(backend, 'name') else type(backend).__name__
        # Extract core components
        cfg = make_serializable(backend.configuration().to_dict())
        props = make_serializable(backend.properties().to_dict()) if hasattr(backend, 'properties') and backend.properties() else {}

        if cfg["n_qubits"] < 10:
            continue

        # Prepare document
        doc = {
            '_id': name,
            'created_at': datetime.datetime.now(datetime.timezone.utc),
            'configuration': cfg,
            'properties': props,
        }

        # Upsert into MongoDB
        collection.replace_one({'_id': name}, doc, upsert=True)
        inserted.append(backend.name)
        print(f"Serialized backend '{name}' into MongoDB.")

    return inserted



def load_backend(name):
    """
    Fetches serialized backend by name from MongoDB and returns an AerSimulator.

    Args:
        name (str): The unique name (_id) of the serialized backend.

    Returns:
        AerSimulator: Simulator configured with the fake backend noise model.
    """
    doc = collection.find_one({'_id': name})
    if not doc:
        raise ValueError(f"No serialized backend found with name '{name}'")

    cfg = AerBackendConfiguration.from_dict(restore_complex(doc['configuration'])) if 'configuration' in doc else None
    props = restore_complex(doc['properties']) if 'properties' in doc else None

    # Create an AER simulator from the backend
    sim = AerSimulator(configuration=cfg, 
                        properties=props)
    return sim


if __name__ == '__main__':
    from quantum_executor import QuantumExecutor

    qe = QuantumExecutor(providers=["local_aer"])
    backends = [b._backend for b in list(qe.virtual_provider.get_backends()["local_aer"].values())]

    print(f"# of backends: {len(backends)}")
    inserted = serialize_backends(backends)

    backends_doc = {"_id": "backends", "backends": inserted}
    collection.insert_one(backends_doc)