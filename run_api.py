#!/usr/bin/env python3
import subprocess
import time

# Run API server
print("Iniciando API...")
proc = subprocess.Popen(["python", "api_app.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Wait for startup
time.sleep(5)

# Check if still running
if proc.poll() is not None:
    print("API no se inició. Salida:")
    output, _ = proc.communicate()
    print(output)
else:
    print("API iniciada correctamente en PID:", proc.pid)
    # Keep it running
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
