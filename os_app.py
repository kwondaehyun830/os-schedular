from flask import Flask, request, jsonify
from scheduler import fcfs_schedule_multi
from scheduler import srtn_schedule_multi

app = Flask(__name__)

@app.route('/api/fcfs', methods=['POST'])
def api_fcfs():
    """
    First‐Come First‐Served 멀티코어 스케줄러
    요청 JSON 구조:
    {
        "processes": [{"pid": "P1", "arrival": 0, "burst": 5}, …],
        "cores": [
        {"id":"E1","type":"E","speed":1,"dyn_power":1,"startup_power":2,"available":0,"state":"off"},
        …
        ]
    }
    """
    data = request.get_json()
    processes = data['processes']
    cores      = data['cores']
    events, total_energy = fcfs_schedule_multi(processes, cores)
    return jsonify({ 'events': events, 'total_energy': total_energy })

@app.route('/api/srtn', methods=['POST'])
def api_srtn():
    """
    Shortest Remaining Time Next (preemptive SJF) 멀티코어 스케줄러
    요청 JSON 구조는 /api/fcfs와 동일합니다.
    """
    data = request.get_json()
    processes = data['processes']
    cores      = data['cores']
    events, total_energy = srtn_schedule_multi(processes, cores)
    return jsonify({ 'events': events, 'total_energy': total_energy })

if __name__ == '__main__':
    app.run(debug=True)
