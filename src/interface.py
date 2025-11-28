import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

import os
from dotenv import dotenv_values, set_key
from pymongo import MongoClient
import math
import json
import subprocess
import threading
import atexit
from pathlib import Path

def close_compose():
    subprocess.run("docker compose down", shell=True)

env_path = ".env"

if not Path(env_path).exists():
    with open(".env", "w") as env:
        env.write("MONGO_INITDB_ROOT_USERNAME=\n" \
        "MONGO_INITDB_ROOT_PASSWORD=\n" \
        "MONGO_DATABASE=\n" \
        "VERSION_NAME=\n" \
        "OUTPUT_DIR='.'\n" \
        "ALGORITHMS=[]\n" \
        "SIZES=[]\n" \
        "BACKENDS=[]\n" \
        "SHOTS=\n" \
        "N_CORES=\n" \
        "JOBS=\n" \
        "LOAD=\n" \
        "MEMFREE=\n" \
        "MEMSUSPEND=\n" \
        "DELAY=\n")
else:
    subprocess.run(["docker", "compose", "up", "-d"])
    atexit.register(close_compose)

config = dotenv_values(env_path)

def display_error(mex):
    terminal_text["state"] = "normal"
    terminal_text.delete(1.0, tk.END)
    terminal_text.insert(1.0, mex, "error")
    terminal_text["state"] = "disabled"

def display_message(mex):
    terminal_text["state"] = "normal"
    terminal_text.delete(1.0, tk.END)
    terminal_text.insert(1.0, mex)
    terminal_text["state"] = "disabled"

root = tk.Tk()

def update_versions():
    global versions
    try:
        vers_file = open(f"{config["OUTPUT_DIR"]}/versions.json", "r")
        versions = json.load(vers_file)
        vers_file.close()
    except FileNotFoundError:
        versions = []
    versions_var.set(versions)

versions_var = tk.StringVar()
update_versions()

algorithms = []
algorithms_var = tk.StringVar()
backends = []
backends_var = tk.StringVar()
sizes = []
sizes_var = tk.StringVar()

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

    if not MONGO_USER or not MONGO_PASSWORD:
        global start_mongo
        start_mongo = False
        algorithms = []
        sizes = []
        backends = []

        algorithms_var.set(algorithms)
        sizes_var.set(sizes)
        backends_var.set(backends)

        return

    client = MongoClient(mongo_url)
    try:
        db_algs = client[DB_NAME_ALGS]
        collection_algs = db_algs[COLLECTION_NAME_ALGS]
    except:
        algorithms = []
        sizes = []

    try:
        algorithms = collection_algs.find_one({"_id": "algorithms"})
        algorithms = algorithms["algorithms"]
    except:
        algorithms = []

    try:
        sizes = collection_algs.find_one({"_id": "sizes"})
        sizes = sizes["sizes"]
    except:
        sizes = []

    try:
        db_backs = client[DB_NAME_BACKS]
        collection_backs = db_backs[COLLECTION_NAME_BACKS]
        backends = collection_backs.find_one({"_id": "backends"})
        backends = backends["backends"]
    except:
        backends = []

    algorithms_var.set(algorithms)
    sizes_var.set(sizes)
    backends_var.set(backends)

get_avaibles()

root.title("QSimBench Dataset Manager")
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
WIDTH = int(screen_w//1.5)
HEIGHT = int(screen_h//1.5)
root.geometry(f"{WIDTH}x{HEIGHT}+{screen_w//2 - WIDTH//2}+{screen_h//2 - HEIGHT//2}")

root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=2)
root.rowconfigure(2, weight=2)

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)

title_frame = tk.Frame(root)
title_frame.grid(row=0, column=0, columnspan=3, sticky="we")

title_frame.columnconfigure(0, weight=1)
title_frame.columnconfigure(1, weight=1)
title_frame.columnconfigure(2, weight=1)

title = tk.Label(title_frame, text="QSimBench Dataset Manager", font=("", int(screen_w//40)))
title.grid(row=0, column=1)

def open_settings():
    SETTINGS_WIDTH = screen_w//4
    SETTINGS_HEIGHT = screen_h//4
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry(f"{SETTINGS_WIDTH}x{SETTINGS_HEIGHT}+{screen_w//2 - SETTINGS_WIDTH//2}+{screen_h//2 - SETTINGS_HEIGHT//2}")
    settings_window.transient(root)
    settings_window.update_idletasks()
    settings_window.grab_set()
    settings_window.focus_set()

    settings_window.rowconfigure(0, weight=1)
    settings_window.rowconfigure(1, weight=1)
    settings_window.rowconfigure(2, weight=1)
    settings_window.rowconfigure(3, weight=1)
    settings_window.rowconfigure(4, weight=1)

    settings_window.columnconfigure(0, weight=1)
    settings_window.columnconfigure(1, weight=1)

    mongo_username = tk.StringVar(value=config["MONGO_INITDB_ROOT_USERNAME"])
    label_username = tk.Label(settings_window, text="MongoDB username:", font=("", int(screen_w / 140)))
    label_username.grid(row=0, column=0)

    entry_username = tk.Entry(settings_window, textvariable=mongo_username, font=("", int(screen_w / 140)))
    entry_username.grid(row=0, column=1)
    entry_username.focus_set()

    mongo_password = tk.StringVar(value=config["MONGO_INITDB_ROOT_PASSWORD"])
    label_password = tk.Label(settings_window, text="MongoDB password:", font=("", int(screen_w / 140)))
    label_password.grid(row=1, column=0)

    entry_password = tk.Entry(settings_window, textvariable=mongo_password, show="*", font=("", int(screen_w / 140)))
    entry_password.grid(row=1, column=1)

    mongo_database = tk.StringVar(value=config["MONGO_DATABASE"])
    label_database = tk.Label(settings_window, text="MongoDB database:", font=("", int(screen_w / 140)))
    label_database.grid(row=2, column=0)

    entry_database = tk.Entry(settings_window, textvariable=mongo_database, font=("", int(screen_w / 140)))
    entry_database.grid(row=2, column=1)

    output_folder = tk.StringVar(value=config["OUTPUT_DIR"])
    label_output = tk.Label(settings_window, text="Output folder:", font=("", int(screen_w / 140)))
    label_output.grid(row=3, column=0)

    button_output = tk.Button(settings_window, text="Choose folder", command=lambda: output_folder.set(filedialog.askdirectory(initialdir=output_folder.get())), font=("", int(screen_w / 140)))
    button_output.grid(row=3, column=1)

    def save_func():
        global config

        set_key(env_path, "OUTPUT_DIR", os.path.realpath(output_folder.get()))

        old_username = config["MONGO_INITDB_ROOT_USERNAME"]
        old_password = config["MONGO_INITDB_ROOT_PASSWORD"]
        old_database = config["MONGO_DATABASE"]

        new_username = mongo_username.get()
        new_password = mongo_password.get()
        new_database = mongo_database.get()

        if not new_username or not new_password or not new_database:
            display_error("Invalid parameter(s)")
            return

        if new_username != old_username or new_password != old_password or new_database != old_database:
            set_key(env_path, "MONGO_INITDB_ROOT_USERNAME", new_username)
            set_key(env_path, "MONGO_INITDB_ROOT_PASSWORD", new_password)
            set_key(env_path, "MONGO_DATABASE", new_database)

            display_message("Changes saved, please restart")
        else:
            display_message("Changes saved")

        config = dotenv_values()

        settings_window.destroy()

    save_button = tk.Button(settings_window, text="Save", command=save_func, font=("", int(screen_w / 140)))
    save_button.grid(row=4, column=0, columnspan=2)

settings_img = Image.open("assets/settings.png")
settings_img = settings_img.resize((int(screen_w//48), int(screen_w//48)), Image.LANCZOS)
settings_pht = ImageTk.PhotoImage(settings_img)
settings = tk.Button(title_frame, image=settings_pht, command=open_settings)
settings.grid(row=0, column=2)

logo_img = Image.open("assets/atom.png")
logo_img = logo_img.resize((int(screen_w//38), int(screen_w//38)), Image.LANCZOS)
logo_pht = ImageTk.PhotoImage(logo_img)
logo = ttk.Label(title_frame, image=logo_pht)
logo.grid(row=0, column=0)

experiment_frame = ttk.Labelframe(root, text="Runs parameters", padding=(10,10), labelanchor="n")
experiment_frame.grid(row=1, column=0, columnspan=3, sticky="we")

experiment_frame.columnconfigure(0, weight=1)
experiment_frame.columnconfigure(1, weight=1)
experiment_frame.columnconfigure(2, weight=1)
experiment_frame.columnconfigure(3, weight=1)
experiment_frame.columnconfigure(4, weight=1)

experiment_frame.rowconfigure(0, weight=1)
experiment_frame.rowconfigure(1, weight=1)

algorithms_frame = ttk.Labelframe(experiment_frame, text="Algorithms", padding=(10,6), labelanchor="n")
algorithms_frame.grid(column=0, row=0, rowspan=2, padx=5, pady=5)

algorithms_frame.rowconfigure(0, weight=1)
algorithms_frame.rowconfigure(1, weight=1)

algorithms_frame.columnconfigure(0, weight=1)
algorithms_frame.columnconfigure(1, weight=1)
algorithms_frame.columnconfigure(2, weight=1)

algorithms_list = tk.Listbox(algorithms_frame, listvariable=algorithms_var, selectmode="multiple", font=("", int(screen_w / 140)), selectbackground="blue", selectforeground="white", exportselection=False, height=7)
algorithms_list.grid(row=1, column=0, columnspan=2, pady=5)

if algorithms:
    selected_algs = json.loads(config["ALGORITHMS"])

    for alg in selected_algs:
        index = algorithms.index(alg)
        algorithms_list.selection_set(index)

algs_button_select = ttk.Button(algorithms_frame, text="Select all", command=lambda: algorithms_list.selection_set(0, tk.END))
algs_button_select.grid(row=0, column=0)

algs_button_deselect = ttk.Button(algorithms_frame, text="Deselect all", command=lambda: algorithms_list.selection_clear(0, tk.END))
algs_button_deselect.grid(row=0, column=1)

algs_scrollbar = ttk.Scrollbar(algorithms_frame, orient="vertical", command=algorithms_list.yview)
algs_scrollbar.grid(row=1, column=2, sticky="ns")
algorithms_list["yscrollcommand"] = algs_scrollbar.set

backends_frame = ttk.Labelframe(experiment_frame, text="Backends", padding=(10,6), labelanchor="n")
backends_frame.grid(column=2, row=0, rowspan=2, padx=5, pady=5)

backends_frame.rowconfigure(0, weight=1)
backends_frame.rowconfigure(1, weight=1)

backends_frame.columnconfigure(0, weight=1)
backends_frame.columnconfigure(1, weight=1)
backends_frame.columnconfigure(2, weight=1)

backends_list = tk.Listbox(backends_frame, listvariable=backends_var, selectmode="multiple", font=("", int(screen_w / 140)), selectbackground="blue", selectforeground="white", exportselection=False, height=7)
backends_list.grid(row=1, column=0, columnspan=2, pady=5)

if backends:
    selected_backends = json.loads(config["BACKENDS"])

    for backend in selected_backends:
        index = backends.index(backend)
        backends_list.selection_set(index)

backs_button_select = ttk.Button(backends_frame, text="Select all", command=lambda: backends_list.selection_set(0, len(backends)-1))
backs_button_select.grid(row=0, column=0)

backs_button_deselect = ttk.Button(backends_frame, text="Deselect all", command=lambda: backends_list.selection_clear(0, len(backends)-1))
backs_button_deselect.grid(row=0, column=1)

backs_scrollbar = ttk.Scrollbar(backends_frame, orient="vertical", command=backends_list.yview)
backs_scrollbar.grid(row=1, column=2, sticky="ns")
backends_list["yscrollcommand"] = backs_scrollbar.set

sizes_frame = ttk.Labelframe(experiment_frame, text="Sizes", padding=(10,6), labelanchor="n")
sizes_frame.grid(column=1, row=0, rowspan=2, padx=5, pady=5)

sizes_frame.rowconfigure(0, weight=1)
sizes_frame.rowconfigure(1, weight=1)

sizes_frame.columnconfigure(0, weight=1)
sizes_frame.columnconfigure(1, weight=1)
sizes_frame.columnconfigure(2, weight=1)

sizes_list = tk.Listbox(sizes_frame, listvariable=sizes_var, selectmode="multiple", font=("", int(screen_w / 140)), selectbackground="blue", selectforeground="white", exportselection=False, height=7)
sizes_list.grid(row=1, column=0, columnspan=2, pady=5)

if sizes:
    selected_sizes = json.loads(config["SIZES"])

    for size in selected_sizes:
        index = sizes.index(size)
        sizes_list.selection_set(index)

sizes_button_select = ttk.Button(sizes_frame, text="Select all", command=lambda: sizes_list.selection_set(0, len(sizes)-1))
sizes_button_select.grid(row=0, column=0)

sizes_button_deselect = ttk.Button(sizes_frame, text="Deselect all", command=lambda: sizes_list.selection_clear(0, len(sizes)-1))
sizes_button_deselect.grid(row=0, column=1)

sizes_scrollbar = ttk.Scrollbar(sizes_frame, orient="vertical", command=sizes_list.yview)
sizes_scrollbar.grid(row=1, column=2, sticky="ns")
sizes_list["yscrollcommand"] = sizes_scrollbar.set

shots_label = tk.Label(experiment_frame, text="Shots:", font=("", int(screen_w / 140)))
shots_label.grid(column=3, row=0)

shots_str = tk.StringVar(value=config["SHOTS"])
shots_entry = tk.Entry(experiment_frame, textvariable=shots_str, font=("", int(screen_w / 140)), width=7)
shots_entry.grid(column=4, row=0)

cores_lable = tk.Label(experiment_frame, text="Cores:\n(per run)", font=("", int(screen_w / 140)))
cores_lable.grid(column=3, row=1)

cores_str = tk.StringVar(value=config["N_CORES"])
cores_entry = tk.Entry(experiment_frame, textvariable=cores_str, font=("", int(screen_w / 140)), width=7)
cores_entry.grid(column=4, row=1)

parallel_frame = ttk.Labelframe(root, text="Parallel parameters", labelanchor="n")
parallel_frame.grid(row=2, column=0, sticky="nsew")

parallel_frame.rowconfigure(0, weight=1)
parallel_frame.rowconfigure(1, weight=1)
parallel_frame.rowconfigure(2, weight=1)
parallel_frame.rowconfigure(3, weight=1)
parallel_frame.rowconfigure(4, weight=1)

parallel_frame.columnconfigure(0, weight=1)
parallel_frame.columnconfigure(1, weight=1)

def add_parallel_label(text, row):
    label = tk.Label(parallel_frame, text=text, font=("", int(screen_w / 140)))
    label.grid(row=row, column=0)

def add_parallel_entry(variable, row):
    entry = tk.Entry(parallel_frame, textvariable=variable, font=("", int(screen_w / 140)), width=7)
    entry.grid(row=row, column=1, padx=5)

jobs_str = tk.StringVar(value=config["JOBS"])
load_str = tk.StringVar(value=config["LOAD"])
memfree_str = tk.StringVar(value=config["MEMFREE"].rstrip("G"))
memsuspend_str = tk.StringVar(value=config["MEMSUSPEND"].rstrip("G"))
delay_str = tk.StringVar(value=config["DELAY"])

add_parallel_label("Jobs:", 0)
add_parallel_label("Load:", 1)
add_parallel_label("Memfree(GB):", 2)
add_parallel_label("Memsuspend(GB):", 3)
add_parallel_label("Delay:", 4)

add_parallel_entry(jobs_str, 0)
add_parallel_entry(load_str, 1)
add_parallel_entry(memfree_str, 2)
add_parallel_entry(memsuspend_str, 3)
add_parallel_entry(delay_str, 4)

buttons_frame = tk.Frame(root)
buttons_frame.grid(row=2, column=2, sticky="nsew")

buttons_frame.rowconfigure(0, weight=1)
buttons_frame.rowconfigure(1, weight=1)

buttons_frame.columnconfigure(0, weight=1)
buttons_frame.columnconfigure(1, weight=1)

version_label = tk.Label(buttons_frame, text="Version name:", font=("", int(screen_w / 140)))
version_label.grid(row=0, column=0)

version_name = tk.StringVar(value=config["VERSION_NAME"])
version_entry = tk.Entry(buttons_frame, textvariable=version_name, font=("", int(screen_w / 140)), width=15)
version_entry.grid(row=0, column=1)

def start_dataset():
    terminal_text.config(state="normal")
    terminal_text.delete(1.0, tk.END)
    terminal_text.config(state="disabled")

    try:
        shots = int(shots_str.get())
        cores = int(cores_str.get())
        jobs = int(jobs_str.get())
        load = int(load_str.get())
        memfree = int(memfree_str.get())
        memsuspend = int(memsuspend_str.get())
        delay = int(delay_str.get())
    except:
        display_error("Invalid parameter(s)")
        return
    
    if  len(version_name.get()) == 0:
        display_error("Invalid version name")
        return

    if version_name.get() in versions:
        display_error("Version name already used")
        return
    else:
        set_key(env_path, "VERSION_NAME", version_name.get())

    chosen_algs = algorithms_list.curselection()
    if chosen_algs:
        set_key(env_path, "ALGORITHMS", json.dumps([algorithms[i] for i in chosen_algs]))
    else:
        set_key(env_path, "ALGORITHMS", "")

    chosen_backs = backends_list.curselection()
    if chosen_backs:
        set_key(env_path, "BACKENDS", json.dumps([backends[i] for i in chosen_backs]))
    else:
        set_key(env_path, "BACKENDS", "")

    chosen_sizes = sizes_list.curselection()
    if chosen_sizes:
        set_key(env_path, "SIZES", json.dumps([sizes[i] for i in chosen_sizes]))
    else:
        set_key(env_path, "SIZES", "")

    set_key(env_path, "SHOTS", str(shots))
    set_key(env_path, "N_CORES", str(cores))
    set_key(env_path, "JOBS", str(jobs))
    set_key(env_path, "LOAD", str(load))
    set_key(env_path, "MEMFREE", str(memfree)+"G")
    set_key(env_path, "MEMSUSPEND", str(memsuspend)+"G")
    set_key(env_path, "DELAY", str(delay))

    def thread_func():
        process = subprocess.Popen(["python", "-u", "new_dataset.py"], stdout=subprocess.PIPE, text=True, bufsize=1)

        for line in process.stdout:
            terminal_text.config(state="normal")
            terminal_text.insert(tk.END, line.strip()+"\n")
            terminal_text.see(tk.END)
            terminal_text.config(state="disabled")
        
        process.wait()

        update_versions()

        start_button["state"] = "normal"
        delete_button["state"] = "normal"

    start_button["state"] = "disabled"
    delete_button["state"] = "disabled"
    thread = threading.Thread(target=thread_func)
    thread.start()

start_button = tk.Button(buttons_frame, text="Start", command=start_dataset, font=("", int(screen_w / 140)))
start_button.grid(row=1, column=0)

def open_delete():
    DELETE_WIDTH = int(screen_w//6.5)
    DELETE_HEIGHT = int(screen_h//4.5)
    delete_window = tk.Toplevel(root)
    delete_window.title("Delete versions")
    delete_window.geometry(f"{DELETE_WIDTH}x{DELETE_HEIGHT}+{screen_w//2 - DELETE_WIDTH//2}+{screen_h//2 - DELETE_HEIGHT//2}")
    delete_window.transient(root)
    delete_window.update_idletasks()
    delete_window.grab_set()
    delete_window.focus_set()

    delete_window.rowconfigure(0, weight=1)
    delete_window.rowconfigure(1, weight=1)
    delete_window.rowconfigure(2, weight=1)

    delete_window.columnconfigure(0, weight=1)
    delete_window.columnconfigure(1, weight=1)
    delete_window.columnconfigure(2, weight=1)

    versions_list = tk.Listbox(delete_window, listvariable=versions_var, selectmode="multiple", selectbackground="blue", selectforeground="white", font=("", int(screen_w / 140)), height=7)
    versions_list.grid(row=0, column=0, columnspan=2)

    versions_scrollbar = ttk.Scrollbar(delete_window, orient="vertical", command=versions_list.yview)
    versions_scrollbar.grid(row=0, column=2, sticky="ns")
    versions_list.config(yscrollcommand=versions_scrollbar.set)

    all_button = tk.Button(delete_window, text="Select all", command=lambda: versions_list.select_set(0, tk.END), font=("", int(screen_w / 140)))
    all_button.grid(row=1, column=0, padx=5, pady=5)

    none_button = tk.Button(delete_window, text="Deselect all", command=lambda: versions_list.select_clear(0, tk.END), font=("", int(screen_w / 140)))
    none_button.grid(row=1, column=1, padx=5, pady=5)

    def delete_versions():
        selected_versions = versions_list.curselection()

        if selected_versions:
            to_delete = []
            for index in selected_versions:
                to_delete.append(versions[index])
            
            delete_button_final.config(state="disabled")
            start_button.config(state="disabled")

            def thread_func():
                process = subprocess.Popen(["python", "remove_versions.py", *to_delete], stdout=subprocess.PIPE, text=True, bufsize=1)

                for line in process.stdout:
                    terminal_text.config(state="normal")
                    terminal_text.insert(tk.END, line.strip()+"\n")
                    terminal_text.see(tk.END)
                    terminal_text.config(state="disabled")
        
                process.wait()

                update_versions()

                delete_button_final.config(state="normal")
                start_button.config(state="normal")

            thread = threading.Thread(target=thread_func)
            thread.start()

    delete_button_final = tk.Button(delete_window, text="Delete versions", command=delete_versions, font=("", int(screen_w / 140)))
    delete_button_final.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

delete_button = tk.Button(buttons_frame, text="Delete versions", command=open_delete, font=("", int(screen_w / 140)))
delete_button.grid(row=1, column=1)

terminal_text = tk.Text(root, height=12, width=60, state="disabled", font=("", int(screen_w / 140)))
terminal_text.grid(row=2, column=1, ipadx=5, ipady=5)
terminal_text.tag_config("error", foreground="red")

root.mainloop()