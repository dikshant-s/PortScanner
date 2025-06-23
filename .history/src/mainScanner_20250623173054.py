#!/usr/bin/env python
import socket
import subprocess
import sys
from datetime import datetime
import json
import os
import threading
import builtins

from multi.scanner_thread import split_processing
import logging
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Function to read and save scan data
def save_scan_data(scan_data):
    
    # File path for storing the last 10 scans
    scans_file = 'scans.json'

    # Check if the file exists and read the existing data
    if os.path.exists(scans_file):
        with open(scans_file, 'r') as file:
            previous_scans = json.load(file)
    else:
        previous_scans = []

    # Append the new scan data
    previous_scans.append(scan_data)

    # Keep only the last 10 scans
    if len(previous_scans) > 10:
        previous_scans = previous_scans[-10:]

    # Save the updated data back to the file
    with open(scans_file, 'w') as file:
        json.dump(previous_scans, file, indent=4)

# Read the absolute path of files
def get_absolute_path(relative_path):
    dir = os.path.dirname(os.path.abspath(__file__))
    split_path = relative_path.split("/")
    absolute_path = os.path.join(dir, *split_path)
    return absolute_path

# Homepage route
@app.route('/')
def homepage():
    # Read the last 10 scans from the JSON file
    scans_file = 'scans.json'

    if os.path.exists(scans_file):
        with open(scans_file, 'r') as file:
            last_10_scans = json.load(file)
    else:
        last_10_scans = []

    return render_template('index.html', last_10_scans=last_10_scans)

# About route
@app.route('/about')
def about():
    return render_template('about.html')

# Contact route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Input route to handle the port scanning
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
        with open(get_absolute_path('../config.json')) as config_file:
            config = json.load(config_file)
            print(get_absolute_path('../config.json'))
        CONST_NUM_THREADS = int(config['thread']['count'])
    except IOError:
        print("config.json file not found")
    except ValueError:
        print("Kindly check the json file for appropriateness of range")

    ports = list(range(range_low, range_high, 1))
    portnum = []

    # Function to scan the ports
    def scan(ports, range_low, range_high):
        try:
            for port in range(range_low, range_high):
                print(f"Scanning port {port}...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((remoteServerIP, port))
                if result == 0:
                    print(f"Port {port}: Open")
                    portnum.append(f"Port {port}")
                sock.close()
        except KeyboardInterrupt:
            print("You pressed Ctrl+C")
            sys.exit()
        except socket.gaierror:
            print('Hostname could not be resolved. Exiting')
            sys.exit()
        except socket.error:
            print("Couldn't connect to server")
            sys.exit()

    # Call the function to handle the multi-threaded scanning
    split_processing(ports, CONST_NUM_THREADS, scan, range_low, range_high)

    # Check the time taken for the scan
    t2 = datetime.now()
    total = t2 - t1

    # Save the scan data to the JSON file
    scan_data = {
        'host': remoteServerIP,
        'range_low': range_low,
        'range_high': range_high,
        'portnum': portnum,
        'time_taken': str(total)
    }

    save_scan_data(scan_data)

    print('Scanning Completed in: ', total)

    # Render the result back on the page
    return render_template('index.html', portnum=portnum, host=remoteServerIP, range_low=range_low, range_high=range_high, total=total)

if __name__ == '__main__':
    app.run(debug=True)
