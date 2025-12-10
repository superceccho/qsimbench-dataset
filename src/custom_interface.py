import customtkinter as ctk

from PIL import Image
from dotenv import dotenv_values, set_key
import os
import json
import subprocess
import atexit
from pymongo import MongoClient
import threading
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("theme.json")

first_time = False

env_path = ".env"

if not os.path.exists(env_path):
    first_time=True

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

config = dotenv_values(env_path)

def display_error(mex):
    response_text.configure(state="normal")
    response_text.insert(ctk.END, "[ERR]" + mex, "red")
    response_text.configure(state="disabled")
    response_text.see(ctk.END)

def display_message(mex):
    response_text.configure(state="normal")
    response_text.insert(ctk.END, mex, "white")
    response_text.configure(state="disabled")
    response_text.see(ctk.END)

def clear_text():
    response_text.configure(state="normal")
    response_text.delete(0.0, ctk.END)
    response_text.configure(state="disabled")

def get_avaibles():
    MONGO_USER = config['MONGO_INITDB_ROOT_USERNAME']
    MONGO_PASSWORD = config['MONGO_INITDB_ROOT_PASSWORD']

    DB_NAME_ALGS = 'quantum_circuit'
    COLLECTION_NAME_ALGS = 'mqt.bench==1.1.9'

    DB_NAME_BACKS = "quantum_backends"
    COLLECTION_NAME_BACKS = "qiskit_fake_backends"

    mongo_url = f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@localhost:27017/'

    global algorithms
    global sizes
    global backends

    client = MongoClient(mongo_url)
    
    db_algs = client[DB_NAME_ALGS]
    collection_algs = db_algs[COLLECTION_NAME_ALGS]

    algorithms = collection_algs.find_one({"_id": "algorithms"})
    algorithms = algorithms["algorithms"]

    sizes = collection_algs.find_one({"_id": "sizes"})
    sizes = sizes["sizes"]

    db_backs = client[DB_NAME_BACKS]
    collection_backs = db_backs[COLLECTION_NAME_BACKS]

    backends = collection_backs.find_one({"_id": "backends"})
    backends = backends["backends"]

WIDTH = 1000
HEIGHT = 600

root = ctk.CTk()
root.update_idletasks()

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

root.geometry(f"{WIDTH}x{HEIGHT}+{screen_w//2 - WIDTH//2}+{screen_h//2 - HEIGHT//2}")
root.title("QSimBench")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=2)
root.rowconfigure(2, weight=2)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

title_label = ctk.CTkLabel(root, text="QSimBench Dataset Manager", font=("DejaVu Sans", 50, "bold"))
title_label.grid(row=0, column=0, columnspan=2)

run_parameters_frame = ctk.CTkFrame(root, fg_color="#3B3B3B")
run_parameters_frame.grid(row=1, column=0, sticky="ew", padx=10, ipadx=5)

run_parameters_frame.rowconfigure(0, weight=1)
run_parameters_frame.rowconfigure(1, weight=1)

run_parameters_frame.columnconfigure(0, weight=1)
run_parameters_frame.columnconfigure(1, weight=1)
run_parameters_frame.columnconfigure(2, weight=1)
run_parameters_frame.columnconfigure(3, weight=1)
run_parameters_frame.columnconfigure(4, weight=1)
run_parameters_frame.columnconfigure(5, weight=1)

def button_selection(button):
    if button.cget("fg_color") == "#242424":
        button.configure(fg_color="#3B3B3B")
    else:
        button.configure(fg_color="#242424")

def select_all(buttons):
    for button in buttons:
        button.configure(fg_color="#3B3B3B")

def deselect_all(buttons):
    for button in buttons:
        button.configure(fg_color="#242424")

algorithms_outer_frame = ctk.CTkFrame(run_parameters_frame, height=100)
algorithms_outer_frame.grid(row=0, column=0, columnspan=2, pady=10)

algorithms_outer_frame.rowconfigure(0, weight=1)
algorithms_outer_frame.rowconfigure(1, weight=1)

algorithms_outer_frame.columnconfigure(0, weight=1)
algorithms_outer_frame.columnconfigure(1, weight=1)

algorithms_inner_frame = ctk.CTkScrollableFrame(algorithms_outer_frame, label_text="Algorithms:")
algorithms_inner_frame.grid(row=0, column=0, columnspan=2)

select_algs = ctk.CTkButton(algorithms_outer_frame, text="Select all", command=lambda: select_all(algorithms_buttons), border_width=0, fg_color="#3B3B3B", width=100)
select_algs.grid(row=1, column=0, padx=5, pady=5)

deselect_algs = ctk.CTkButton(algorithms_outer_frame, text="Deselect all", command=lambda: deselect_all(algorithms_buttons), border_width=0, fg_color="#3B3B3B", width=100)
deselect_algs.grid(row=1, column=1, padx=5, pady=5)

sizes_outer_frame = ctk.CTkFrame(run_parameters_frame)
sizes_outer_frame.grid(row=0, column=2, columnspan=2)

sizes_outer_frame.rowconfigure(0, weight=1)
sizes_outer_frame.rowconfigure(1, weight=1)

sizes_outer_frame.columnconfigure(0, weight=1)
sizes_outer_frame.columnconfigure(1, weight=1)

sizes_inner_frame = ctk.CTkScrollableFrame(sizes_outer_frame, label_text="Sizes:")
sizes_inner_frame.grid(row=0, column=0, columnspan=2)

select_sizes = ctk.CTkButton(sizes_outer_frame, text="Select all", command=lambda: select_all(sizes_buttons), width=100, fg_color="#3B3B3B", border_width=0)
select_sizes.grid(row=1, column=0, padx=5, pady=5)

deselect_sizes = ctk.CTkButton(sizes_outer_frame, text="Deselect all", command=lambda: deselect_all(sizes_buttons), width=100, fg_color="#3B3B3B", border_width=0)
deselect_sizes.grid(row=1, column=1, padx=5, pady=5)

backends_outer_frame = ctk.CTkFrame(run_parameters_frame)
backends_outer_frame.grid(row=0, column=4, columnspan=2)

backends_outer_frame.rowconfigure(0, weight=1)
backends_outer_frame.rowconfigure(1, weight=1)

backends_outer_frame.columnconfigure(0, weight=1)
backends_outer_frame.columnconfigure(1, weight=1)

backends_inner_frame = ctk.CTkScrollableFrame(backends_outer_frame, label_text="Backends:")
backends_inner_frame.grid(row=0, column=0 ,columnspan=2)

select_backs = ctk.CTkButton(backends_outer_frame, text="Select all", command=lambda: select_all(backends_buttons), width=100, fg_color="#3B3B3B", border_width=0)
select_backs.grid(row=1, column=0, padx=5, pady=5)

deselect_backs = ctk.CTkButton(backends_outer_frame, text="Deselect all", command=lambda: deselect_all(backends_buttons), width=100, fg_color="#3B3B3B", border_width=0)
deselect_backs.grid(row=1, column=1, padx=5, pady=5)

shots_label = ctk.CTkLabel(run_parameters_frame, text="Shots count:", fg_color="#3B3B3B")
shots_label.grid(row=1, column=0)

shots_entry = ctk.CTkEntry(run_parameters_frame, border_width=0, width=100)
shots_entry.insert(0, config["SHOTS"])
shots_entry.grid(row=1, column=1, pady=5)

cores_label = ctk.CTkLabel(run_parameters_frame, text="Cores per run:", fg_color="#3B3B3B")
cores_label.grid(row=1, column=2)

cores_entry = ctk.CTkEntry(run_parameters_frame, width=100, border_width=0)
cores_entry.insert(0, config["N_CORES"])
cores_entry.grid(row=1, column=3, pady=5)

version_label = ctk.CTkLabel(run_parameters_frame, text="Version name:", fg_color="#3B3B3B")
version_label.grid(row=1, column=4)

version_entry = ctk.CTkEntry(run_parameters_frame, border_width=0, width=100)
version_entry.insert(0, config["VERSION_NAME"])
version_entry.grid(row=1, column=5, pady=5)

parallel_parameters_frame = ctk.CTkFrame(root, fg_color="#3B3B3B", height=355)
parallel_parameters_frame.grid_propagate(False)
parallel_parameters_frame.grid(row=1, column=1, sticky="ew", padx=5)

parallel_parameters_frame.rowconfigure(0, weight=1)
parallel_parameters_frame.rowconfigure(1, weight=1)
parallel_parameters_frame.rowconfigure(2, weight=1)
parallel_parameters_frame.rowconfigure(3, weight=1)
parallel_parameters_frame.rowconfigure(4, weight=1)
parallel_parameters_frame.rowconfigure(5, weight=1)

parallel_parameters_frame.columnconfigure(0, weight=1)
parallel_parameters_frame.columnconfigure(1, weight=1)

parallel_label = ctk.CTkLabel(parallel_parameters_frame, text="Parallel parameters:", corner_radius=5)
parallel_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10)

jobs_label = ctk.CTkLabel(parallel_parameters_frame, text="Jobs:", fg_color="#3B3B3B")
jobs_label.grid(row=1, column=0)

jobs_entry = ctk.CTkEntry(parallel_parameters_frame, border_width=0, width=100)
jobs_entry.insert(0, config["JOBS"])
jobs_entry.grid(row=1, column=1)

load_label = ctk.CTkLabel(parallel_parameters_frame, text="Load:", fg_color="#3B3B3B")
load_label.grid(row=2, column=0)

load_entry = ctk.CTkEntry(parallel_parameters_frame, border_width=0, width=100)
load_entry.insert(0, config["LOAD"])
load_entry.grid(row=2, column=1)

memfree_label = ctk.CTkLabel(parallel_parameters_frame, text="Memfree:", fg_color="#3B3B3B")
memfree_label.grid(row=3, column=0)

memfree_entry = ctk.CTkEntry(parallel_parameters_frame, border_width=0, width=100)
memfree_entry.insert(0, config["MEMFREE"])
memfree_entry.grid(row=3, column=1)

memsuspend_label = ctk.CTkLabel(parallel_parameters_frame, text="Memsuspend", fg_color="#3B3B3B")
memsuspend_label.grid(row=4, column=0)

memsuspend_entry = ctk.CTkEntry(parallel_parameters_frame, border_width=0, width=100)
memsuspend_entry.insert(0, config["MEMSUSPEND"])
memsuspend_entry.grid(row=4, column=1)

delay_label = ctk.CTkLabel(parallel_parameters_frame, text="Delay:", fg_color="#3B3B3B")
delay_label.grid(row=5, column=0)

delay_entry = ctk.CTkEntry(parallel_parameters_frame, border_width=0, width=100)
delay_entry.insert(0, config["DELAY"])
delay_entry.grid(row=5, column=1)

lower_frame = ctk.CTkFrame(root)
lower_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

lower_frame.columnconfigure(0, weight=1)
lower_frame.columnconfigure(1, weight=2)
lower_frame.columnconfigure(2, weight=1)

lower_frame.rowconfigure(0, weight=1)
lower_frame.rowconfigure(1, weight=1)

response_text = ctk.CTkTextbox(lower_frame, width=450, height=90)
response_text.configure(state="disabled")
response_text.grid(row=0, column=1, pady=5)
response_text.tag_config("white", foreground="white")
response_text.tag_config("red", foreground="red")

def open_delete():
    DELETE_WIDTH = 500
    DELETE_HEIGHT = 350
    delete_window = ctk.CTkToplevel(root)
    delete_window.title("Settings")
    delete_window.geometry(f"{DELETE_WIDTH}x{DELETE_HEIGHT}+{screen_w//2 - DELETE_WIDTH//2}+{screen_h//2 - DELETE_HEIGHT//2}")
    delete_window.transient(root)
    delete_window.update_idletasks()
    delete_window.grab_set()
    delete_window.focus_set()

    delete_outer_frame = ctk.CTkFrame(delete_window, fg_color="#3B3B3B")
    delete_outer_frame.pack(pady=5)

    delete_outer_frame.rowconfigure(0, weight=1)
    delete_outer_frame.rowconfigure(1, weight=1)

    delete_outer_frame.columnconfigure(0, weight=1)
    delete_outer_frame.columnconfigure(1, weight=1)

    delete_inner_frame = ctk.CTkScrollableFrame(delete_outer_frame, label_text="Versions:")
    delete_inner_frame.grid(row=0, column=0, columnspan=2, pady=5)

    buttons = []
    for version in versions:
        button = ctk.CTkButton(delete_inner_frame, text=version, border_width=0, corner_radius=0)
        button.configure(command=lambda b=button: button_selection(b))
        button.pack(fill=ctk.X)
        buttons.append(button)

    select_button = ctk.CTkButton(delete_outer_frame, text="Select all", command=lambda b=buttons: select_all(b), border_width=0)
    select_button.grid(row=1, column=0, padx=5, pady=5)

    deselect_button = ctk.CTkButton(delete_outer_frame, text="Select all", command=lambda b=buttons: deselect_all(b), border_width=0)
    deselect_button.grid(row=1, column=1, padx=5, pady=5)

    def delete_func():
        chosen_versions = []
        for button in buttons:
            if button.cget("fg_color") == "#3B3B3B":
                chosen_versions.append(button.cget("text"))

        if not chosen_versions:
            clear_text()
            display_error("No versions chosen")
            return
        
        def thread_func():
            start_button.configure(state="disabled")
            delete_button.configure(state="disabled")

            clear_text()

            process = subprocess.Popen(["python", "-u", "remove_versions.py", *chosen_versions], stdout=subprocess.PIPE, text=True, bufsize=1)

            for line in process.stdout:
                *rest, last = line.strip().rsplit(" ", 1)
                if last == "failed":
                    display_error(line)
                else:
                    display_message(line)

                response_text.see(ctk.END)
            
            process.wait()

            for version in chosen_versions:
                versions.remove(version)

            for button in buttons:
                if button.cget("text") in chosen_versions:
                    button.destroy()

            display_message(f"Versions {", ".join(chosen_versions)} deleted")

            start_button.configure(state="normal")
            delete_button.configure(state="normal")

        thread = threading.Thread(target=thread_func)
        thread.start()

    delete_button = ctk.CTkButton(delete_window, text="Delete versions", image=delete_img, command=delete_func)
    delete_button.pack(pady=5)

    delete_window.mainloop()

delete_img = ctk.CTkImage(dark_image=Image.open("assets/trash_dark.png"), size=(30,30))
delete_button = ctk.CTkButton(lower_frame, text="Delete versions", image=delete_img, command=open_delete)
delete_button.configure(state="disabled")
delete_button.grid(row=0, column=0, rowspan=2)

versions = []
vers_path = f"{config['OUTPUT_DIR']}/versions.json"
if os.path.exists(vers_path):
    with open(vers_path, "r") as file:
        versions = json.load(file)

def start_func():
    clear_text()
    
    error=False

    chosen_algorithms = []
    for button in algorithms_buttons:
        if button.cget("fg_color") == "#3B3B3B":
            chosen_algorithms.append(button.cget("text"))

    if not chosen_algorithms:
        display_error("No algorithms selected\n")
        error=True
    
    chosen_sizes = []
    for button in sizes_buttons:
        if button.cget("fg_color") == "#3B3B3B":
            chosen_sizes.append(button.cget("text"))
            
    if not chosen_sizes:
        display_error("No sizes selected\n")
        error=True
    
    chosen_backends = []
    for button in backends_buttons:
        if button.cget("fg_color") == "#3B3B3B":
            chosen_backends.append(button.cget("text"))
            
    if not chosen_backends:
        display_error("No backends selected\n")
        error=True
    
    shots = shots_entry.get().strip().lstrip("0")
    if not shots.isdigit():
        display_error("Invalid shots count\n")
        error=True

    cores = cores_entry.get().strip().lstrip("0")
    if not cores.isdigit() and not cores == "all":
        display_error("Invalid cores count\n")
        error=True

    jobs = jobs_entry.get().strip().lstrip("0")
    if not jobs.isdigit():
        display_error("Invalid jobs parameter\n")
        error=True

    load = load_entry.get().strip().lstrip("0")
    if not load.isdigit():
        display_error("Invalid load parameter\n")
        error=True

    regex = "^[0-9]+([KMGTPkmgpt])?$"
    
    memfree = memfree_entry.get().strip()
    if not re.match(regex, memfree) or (len(memfree) > 2 and memfree[0] == "0"):
        display_error("Invalid memfree parameter\n")
        error=True

    memsuspend = memsuspend_entry.get().strip()
    if not re.match(regex, memsuspend) or (len(memsuspend) > 2 and memsuspend == "0"):
        display_error("Invalid memsuspend parameter\n")
        error=True
    
    delay = delay_entry.get().strip()
    if not delay.isdigit():
        display_error("Invalid delay parameter\n")
        error=True

    new_name = version_entry.get().strip()
    if not new_name or " " in new_name:
        display_error("Invalid versions name\n")
        error=True
    if new_name in versions:
        display_error("Version name already used\n")
        error=True

    if error:
        response_text.see(ctk.END)
        return
    
    set_key(env_path, "ALGORITHMS", json.dumps(chosen_algorithms))
    set_key(env_path, "SIZES", json.dumps(chosen_sizes))
    set_key(env_path, "BACKENDS", json.dumps(chosen_backends))
    set_key(env_path, "SHOTS", str(shots))
    set_key(env_path, "N_CORES", str(cores))
    set_key(env_path, "JOBS", str(jobs))
    set_key(env_path, "LOAD", str(load))
    set_key(env_path, "MEMFREE", str(memfree))
    set_key(env_path, "MEMSUSPEND", str(memsuspend))
    set_key(env_path, "DELAY", str(delay))
    set_key(env_path, "VERSION_NAME", new_name)

    try:
        os.remove("errors.txt")
        os.remove("times.txt")
    except:
        pass

    runs_count = len(chosen_algorithms) * len(chosen_sizes) * len(chosen_backends)
    bar_step = 1 / runs_count

    progress_bar = ctk.CTkProgressBar(lower_frame, width=450, height=15)
    progress_bar.set(0)
    progress_bar.grid(row=1, column=1, pady=5)

    def thread_func():
        start_button.configure(state="disabled")
        delete_button.configure(state="disabled")

        clear_text()
        display_message("Starting...\n")
        process = subprocess.Popen(["python", "-u", "new_dataset.py"], stdout=subprocess.PIPE, text=True, bufsize=1)

        response_text.configure(text_color="white")
        for line in process.stdout:
            *rest, last = line.strip().rsplit(" ", 1)
            if last == "failed":
                display_error(line)
            else:
                display_message(line)
            response_text.see(ctk.END)

            progress_bar.set(progress_bar.get() + bar_step)
        
        process.wait()

        display_message(f"Done, version {new_name} created")
        versions.append(new_name)
        start_button.configure(state="normal")
        delete_button.configure(state="normal")

        progress_bar.destroy()
        
    thread = threading.Thread(target=thread_func)
    thread.start()
    
start_img = ctk.CTkImage(dark_image=Image.open("assets/atom_dark.png"), size=(30,30))
start_button = ctk.CTkButton(lower_frame, text="Start", command=start_func, image=start_img)
start_button.configure(state="disabled")
start_button.grid(row=0, column=2, rowspan=2)

algorithms = []
sizes = []
backends = []

algorithms_buttons = []
sizes_buttons = []
backends_buttons = []

def init_func():

    def close_compose():
        subprocess.run(["docker", "compose", "down"])
    
    display_message("Starting docker compose...\n")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    atexit.register(close_compose)

    if first_time:
        progress_bar = ctk.CTkProgressBar(lower_frame, width=450, height=15)
        progress_bar.grid(row=1, column=1, pady=5)

        display_message("Serializing circuits...\n")
        progress_bar.set(0)
        process = subprocess.Popen(["python", "-u", "utils/serialise_qc.py"], stdout=subprocess.PIPE, text=True, bufsize=1)
        *_, count = process.stdout.readline().rsplit(" ")
        count = int(count)
        bar_step = 1 / count

        for _ in process.stdout:
            progress_bar.set(progress_bar.get() + bar_step)

        display_message("Circuits serialized\n")

        display_message("Serializing backends...\n")
        progress_bar.set(0)
        process = subprocess.Popen(["python", "-u", "utils/serialise_qpu.py"], stdout=subprocess.PIPE, text=True, bufsize=1)
        *_, count = process.stdout.readline().rsplit(" ")
        count = int(count)
        bar_step = 1 / count

        for _ in process.stdout:
            progress_bar.set(progress_bar.get() + bar_step)

        display_message("Backends serialized\n")

        progress_bar.destroy()

    get_avaibles()
    
    for algorithm in algorithms:
        button = ctk.CTkButton(algorithms_inner_frame, text=algorithm, corner_radius=0, border_width=0, fg_color="#3B3B3B" if algorithm in json.loads(config["ALGORITHMS"]) else "#242424", hover_color="#3B3B3B")
        button.configure(command=lambda b=button: button_selection(b))
        button.pack(fill=ctk.X)
        algorithms_buttons.append(button)

    for size in sizes:
        button = ctk.CTkButton(sizes_inner_frame, text=size, corner_radius=0, border_width=0, fg_color="#3B3B3B" if size in json.loads(config["SIZES"]) else "#242424", hover_color="#3B3B3B")
        button.configure(command=lambda b=button: button_selection(b))
        sizes_buttons.append(button)
        button.pack(fill=ctk.X)

    for backend in backends:
        button = ctk.CTkButton(backends_inner_frame, text=backend, corner_radius=0, border_width=0, fg_color="#3B3B3B" if backend in json.loads(config["BACKENDS"]) else "#242424", hover_color="#3B3B3B")
        button.configure(command=lambda b=button: button_selection(b))
        button.pack(fill=ctk.X)
        backends_buttons.append(button)

    start_button.configure(state="normal")
    delete_button.configure(state="normal")

    clear_text()
    display_message("Ready!")
    
init_thread = threading.Thread(target=init_func)
init_thread.start()

root.mainloop()