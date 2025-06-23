#!/usr/bin/env python
import socket
import subprocess
import sys
from datetime import datetime
import json
import os
import threading
import builtins
import logging
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ✅ Integrated split_processing (no need for multi folder)
def split_processing(data, num_threads, func, *args):
    length = len(data)
    chunk_size = length // num_threads
    threads = []

    for i in range(num_threads):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_threads - 1 else length
        thread = threading.Thread(target=func, args=(data, start, end, *args))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# ✅ Function to read and save scan data
def save_scan_data(scan_data):
    scans_file = 'scans.json'
    if os.path.exists(scans_file):
        with open(scans_file, 'r') as file:
            previous_scans = json.load(file)
    else:
        previous_scans = []
    previous_scans.append(scan_data)
    if len(previous_scans) > 10:
        previous_scans = previous_scans[-10:]
    with open(scans_file, 'w') as file:
        json.dump(previous_scans, file, indent=4)

# ✅ Read the absolute path of files
def get_absolute_path(relative_path):
    dir = os.path.dirname(os.path.abspath(__file__))
    split_path = relative_path.split("/")
    return os.path.join(dir, *split_path)

# ✅ Homepage route
@app.route('/')
def homepage():
    scans_file = 'scans.json'
    if os.path.exists(scans_file):
        with open(scans_file, 'r') as file:
            last_10_scans = json.load(file)
    else:
        last_10_scans = []
    return render_template('index.html', last_10_scans=last_10_scans)

# ✅ About route
@app.route('/about')
def about():
    return render_template('about.html')

# ✅ Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# ✅ Input route
@app.route('/input', methods=["POST"])
def input():
    if request.method == "POST":
        remoteServer = request.form["host"]
        remoteServerIP = socket.gethostbyname(remoteServer)
        range_low = int(request.form["range_low"])
        range_high = int(request.form["range_high"])
    else:
        return EnvironmentError

    print("-" * 60)
    print("Please wait, scanning remote host....", remoteServerIP)
    print("-" * 60)

    t1 = datetime.now()

    try:
        with open(get_absolute_path('config.json')) as config_file:
            config = json.load(config_file)
        CONST_NUM_THREADS = int(config['thread']['count'])
    except IOError:
        print("config.json file not found")
        CONST_NUM_THREADS = 4
    except ValueError:
        print("Check your JSON file")
        CONST_NUM_THREADS = 4

    ports = list(range(range_low, range_high, 1))
    portnum = []

    # ✅ Port scanning function
    def scan(ports, start, end):
        try:
            for i in range(start, end):
                port = ports[i]
                print(f"Scanning port {port}...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((remoteServerIP, port))
                if result == 0:
                    print(f"Port {port}: Open")
                    portnum.append(f"Port {port}")
                sock.close()
        except Exception as e:
            print("Error:", e)
            sys.exit()

    # ✅ Run threaded scan
    split_processing(ports, CONST_NUM_THREADS, scan)

    t2 = datetime.now()
    total = t2 - t1

    # ✅ Save result
    scan_data = {
        'host': remoteServerIP,
        'range_low': range_low,
        'range_high': range_high,
        'portnum': portnum,
        'time_taken': str(total)
    }
    save_scan_data(scan_data)

    print('Scanning Completed in: ', total)

    return render_template('index.html', portnum=portnum, host=remoteServerIP, range_low=range_low, range_high=range_high, total=total)

# ✅ Run locally
if __name__ == '__main__':
    app.run(debug=True)
