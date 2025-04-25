import threading
from flask import Flask, request, jsonify, send_from_directory
import webview
from scheduler import fcfs_schedule_multi

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static','index.html')

@app.route('/api/fcfs', methods=['POST'])
def api_fcfs():
    data = request.json
    procs = data['processes']
    # cores 세팅
    cores = ([{'id':f'P{i+1}','type':'P','available':0} for i in range(data['pcores'])] +
            [{'id':f'E{i+1}','type':'E','available':0} for i in range(data['ecores'])])
    sched = fcfs_schedule_multi(procs, cores)
    return jsonify(sched)

if __name__=='__main__':
    threading.Thread(target=lambda: app.run()).start()
    webview.create_window('OS Scheduler','http://127.0.0.1:5000',width=1200,height=800)
    webview.start()

