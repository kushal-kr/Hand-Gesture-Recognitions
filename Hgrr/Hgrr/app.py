from flask import Flask, render_template, jsonify
import subprocess
import os
import signal
import psutil
import sys

app = Flask(__name__)

# Store the current running process
current_process = None

@app.route('/')
def index():
    return render_template('index.html')

def terminate_current_process():
    global current_process
    if current_process and current_process.poll() is None:
        try:
            # Get the process group ID on Windows
            if sys.platform == 'win32':
                # On Windows, we need to terminate the process and its children
                parent = psutil.Process(current_process.pid)
                for child in parent.children(recursive=True):
                    try:
                        child.terminate()
                    except:
                        pass
                parent.terminate()
            else:
                # On Unix-like systems, we can use process groups
                os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            
            current_process = None
            return True
        except Exception as e:
            print(f"Error terminating process: {e}")
            return False
    return True

@app.route('/terminate_current')
def terminate_current():
    if terminate_current_process():
        return jsonify({"status": "success", "message": "Process terminated successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to terminate process"})

@app.route('/run_camera')
def run_camera():
    global current_process
    terminate_current_process()
    current_process = subprocess.Popen(['python', 'camera.py'], 
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0)
    return jsonify({"status": "success", "message": "Camera script launched"})

@app.route('/run_youtube')
def run_youtube():
    global current_process
    terminate_current_process()
    current_process = subprocess.Popen(['python', 'youtube.py'], 
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0)
    return jsonify({"status": "success", "message": "Youtube script launched"})

@app.route('/run_mouse')
def run_mouse():
    global current_process
    terminate_current_process()
    current_process = subprocess.Popen(['python', 'mousic.py'], 
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0)
    return jsonify({"status": "success", "message": "Mouse script launched"})

@app.route('/run_ppt')
def run_ppt():
    global current_process
    terminate_current_process()
    current_process = subprocess.Popen(['python', 'ppt.py'], 
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0)
    return jsonify({"status": "success", "message": "PPT script launched"})

@app.route('/run_volume')
def run_volume():
    global current_process
    terminate_current_process()
    current_process = subprocess.Popen(['python', 'volume.py'], 
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0)
    return jsonify({"status": "success", "message": "Volume script launched"})

@app.route('/run_signlanguage')
def run_signlanguage():
    global current_process
    terminate_current_process()
    current_process = subprocess.Popen(['python', 'signlanguage.py'], 
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0)
    return jsonify({"status": "success", "message": "Sign Language script launched"})

if __name__ == '__main__':
    app.run(debug=True)