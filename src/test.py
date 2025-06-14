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

@app.route('/')
def homepage():
    return render_template('page.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

def homepage():
    return render_template('index.html')

exc = getattr(builtins, "IOError", FileNotFoundError)

# Clear the screen
# subprocess.call('clear', shell=True)

@app.route('/input', methods=["POST"])
def input():
    # Ask for input
    if request.method == "POST":
        remoteServer = request.form["host"]
        remoteServerIP = socket.gethostbyname(remoteServer)
        range_low = int(request.form["range_low"])
        range_high = int(request.form["range_high"])
    else:
        return EnvironmentError

    # Print a nice banner with information on which host we are about to scan
    print("-" * 60)
    print("Please wait, scanning remote host....", remoteServerIP)
    print("-" * 60)

    def get_absolute_path(relative_path):
        dir = os.path.dirname(os.path.abspath(__file__))
        split_path = relative_path.split("/")
        absolute_path = os.path.join(dir, *split_path)
        return absolute_path

    # Check what time the scan started
    t1 = datetime.now()

    # Getting port range values from config.json
    try:
        with open(get_absolute_path('../config.json')) as config_file:
            config = json.load(config_file)
            print(get_absolute_path('../config.json'))
        # defining number of threads running concurrently
        CONST_NUM_THREADS = int(config['thread']['count'])

    except IOError:
        print("config.json file not found")
    except ValueError:
        print("Kindly check the json file for appropriateness of range")

    ports = list(range(range_low, range_high, 1))
    # scanning the port only in range of (range_low, range_high)

    portnum = []

    def scan(ports, range_low, range_high):
        try:
            for port in range(range_low, range_high):
                print(f"Scanning port {port}...")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((remoteServerIP, port))
                if result == 0:
                    print("Port {}: 	 Open".format(port))
                    portnum.append("Port "+str(port))
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

    # calling function from scanner_thread.py for multithreading
    split_processing(ports, CONST_NUM_THREADS, scan, range_low, range_high)

    # Checking the time again
    t2 = datetime.now()

    # Calculates the difference of time, to see how long it took to run the script
    total = t2 - t1

    # Printing the information to screen
    print('Scanning Completed in: ', total)
    return render_template('index.html', portnum=portnum, host=remoteServerIP, range_low=range_low, range_high=range_high, total=total)

@app.route('/simulate_ddos', methods=["POST"])
def simulate_ddos():
    if request.method == "POST":
        target_ip = request.form["host"]  # Target host
        target_port = int(request.form["port"])  # Target port
        num_threads = int(request.form.get("threads", 500))  # Default to 500 threads if not specified

        # Start the DDoS simulation
        os.system(f"python ddos_simulation.py {target_ip} {target_port} {num_threads}")
        
        return render_template("index.html", message="DDoS simulation started!")

if __name__ == '__main__':
    app.run(debug=True)
