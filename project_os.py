import sys
import tkinter as tk
from tkinter import messagebox

# 전역 변수
arrival_entries = []
burst_entries = []
schedule = []  # 각 프로세스별 스케줄 정보 리스트
cores = []     # 각 코어 정보 리스트
simulation_time = 0
simulation_marker = None

# 전력 소비 단가 (W per second)
P_POWER = 5   # P-코어 1초당 5W
E_POWER = 1   # E-코어 1초당 1W

def reset_all():
    global arrival_entries, burst_entries, schedule, cores, simulation_time, simulation_marker
    # 동적 입력 필드 초기화
    for w in input_frame.winfo_children():
        w.destroy()
    arrival_entries = []
    burst_entries = []
    # 스케줄, 코어, 시뮬레이션 초기화
    schedule = []
    cores = []
    simulation_time = 0
    if simulation_marker:
        canvas.delete(simulation_marker)
    canvas.delete("all")
    # 입력 필드 초기화
    num_processes_entry.delete(0, tk.END)
    p_cores_entry.delete(0, tk.END)
    e_cores_entry.delete(0, tk.END)
    # 결과 텍스트와 상태 레이블 초기화
    result_text.delete("1.0", tk.END)
    sim_label.config(text="시뮬레이션 대기중")

def fcfs_schedule_multi(processes, cores):
    """
    FCFS 멀티코어 스케줄링
    processes: {'pid','arrival','burst'}
    cores: [{'id','type','available'}]
    """
    sched = []
    procs = sorted(processes, key=lambda p: p['arrival'])
    for proc in procs:
        core = min(cores, key=lambda c: c['available'])
        start = max(proc['arrival'], core['available'])
        finish = start + proc['burst']
        sched.append({
            'pid': proc['pid'],
            'arrival': proc['arrival'],
            'burst': proc['burst'],
            'start': start,
            'finish': finish,
            'core': core['id'],
            'ctype': core['type']
        })
        core['available'] = finish
    return sched

def draw_gantt_chart(canvas, schedule, cores):
    canvas.delete("all")
    time_scale = 50
    x_offset = 100
    row_height = 40
    for i, core in enumerate(cores):
        y_top = 50 + i * row_height
        y_bottom = y_top + row_height - 10
        canvas.create_text(50, (y_top+y_bottom)/2, text=core['id'], font=("Arial", 10, "bold"))
        for entry in schedule:
            if entry['core'] != core['id']:
                continue
            x1 = x_offset + entry['start'] * time_scale
            x2 = x_offset + entry['finish'] * time_scale
            canvas.create_rectangle(x1, y_top, x2, y_bottom, fill="skyblue", outline="black")
            canvas.create_text((x1+x2)/2, (y_top+y_bottom)/2,
                               text=entry['pid'], font=("Arial", 10, "bold"))
    if schedule:
        t_max = max(e['finish'] for e in schedule)
        for t in range(int(t_max)+1):
            x = x_offset + t * time_scale
            canvas.create_line(x, 40, x, 50+len(cores)*row_height, fill="#ccc")
            canvas.create_text(x, 40, text=str(t), font=("Arial", 8))

def compute_schedule():
    global schedule, cores
    try:
        n = int(num_processes_entry.get())
        pc = int(p_cores_entry.get())
        ec = int(e_cores_entry.get())
    except ValueError:
        messagebox.showerror("입력 오류", "모든 개수는 정수로 입력해야 합니다.")
        return
    if pc + ec == 0 or pc + ec > 4:
        messagebox.showerror("입력 오류", "P/E 코어 합은 1~4 사이여야 합니다.")
        return

    processes = []
    for i in range(n):
        try:
            arrival = float(arrival_entries[i].get())
            burst = float(burst_entries[i].get())
        except ValueError:
            messagebox.showerror("입력 오류", "도착시간과 실행시간은 숫자여야 합니다.")
            return
        processes.append({"pid": f"P{i+1}", "arrival": arrival, "burst": burst})
    cores = []
    for i in range(pc):
        cores.append({"id": f"P{i+1}", "type": "P", "available": 0})
    for i in range(ec):
        cores.append({"id": f"E{i+1}", "type": "E", "available": 0})

    schedule = fcfs_schedule_multi(processes, cores)

    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, "FCFS 멀티코어 스케줄링 결과:\n")
    for e in schedule:
        result_text.insert(tk.END,
            f"{e['pid']} (Core {e['core']}) - 도착 {e['arrival']}, 실행 {e['burst']}, "
            f"시작 {e['start']}, 종료 {e['finish']}\n")

    n = len(schedule)
    waits = [e['start'] - e['arrival'] for e in schedule]
    turns = [e['finish'] - e['arrival'] for e in schedule]
    avg_wait = sum(waits)/n
    avg_turn = sum(turns)/n
    result_text.insert(tk.END, f"\n평균 대기 시간: {avg_wait:.2f}\n평균 반환 시간: {avg_turn:.2f}\n")

    p_energy = sum(e['burst'] * P_POWER for e in schedule if e['ctype']=="P")
    e_energy = sum(e['burst'] * E_POWER for e in schedule if e['ctype']=="E")
    result_text.insert(tk.END,
        f"\n전력 소비 (P-코어): {p_energy:.1f} W·s\n전력 소비 (E-코어): {e_energy:.1f} W·s\n")

    draw_gantt_chart(canvas, schedule, cores)

def generate_input_fields():
    global arrival_entries, burst_entries
    try:
        num = int(num_processes_entry.get())
    except ValueError:
        messagebox.showerror("입력 오류", "프로세스 개수는 정수여야 합니다.")
        return
    for w in input_frame.winfo_children():
        w.destroy()
    arrival_entries = []
    burst_entries = []
    header = tk.Frame(input_frame)
    header.pack(fill="x")
    tk.Label(header, text="PID", width=5).grid(row=0, column=0)
    tk.Label(header, text="도착시간", width=10).grid(row=0, column=1)
    tk.Label(header, text="실행시간", width=10).grid(row=0, column=2)
    for i in range(num):
        row = tk.Frame(input_frame)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"P{i+1}", width=5).grid(row=0, column=0)
        a = tk.Entry(row, width=10); a.grid(row=0, column=1, padx=5)
        b = tk.Entry(row, width=10); b.grid(row=0, column=2, padx=5)
        arrival_entries.append(a)
        burst_entries.append(b)

def update_simulation():
    global simulation_time, simulation_marker
    if simulation_marker is not None:
        canvas.delete(simulation_marker)
    x = 100 + simulation_time * 50
    height = 50 + len(cores)*40
    simulation_marker = canvas.create_line(x, 30, x, height, fill="red", width=2)
    current = "Idle"
    for e in schedule:
        if simulation_time >= e['start'] and simulation_time < e['finish']:
            current = f"{e['pid']} @ {e['core']}"
            break
    sim_label.config(text=f"시간: {simulation_time}s | 실행 중: {current}")
    t_max = max((e['finish'] for e in schedule), default=0)
    if simulation_time < t_max:
        simulation_time += 1
        root.after(1000, update_simulation)

def start_simulation():
    global simulation_time, simulation_marker
    simulation_time = 0
    if simulation_marker:
        canvas.delete(simulation_marker)
    update_simulation()

# 메인 윈도우
root = tk.Tk()
root.title("프로세스 스케줄링 시뮬레이터")
root.geometry("1200x700")

# 좌측: 입력
left = tk.Frame(root, width=300)
left.pack(side="left", fill="y", padx=10, pady=10)

tk.Label(left, text="프로세스 개수:").pack(anchor="w")
num_processes_entry = tk.Entry(left, width=5); num_processes_entry.pack(anchor="w")
tk.Label(left, text="P-코어 개수:").pack(anchor="w", pady=(10,0))
p_cores_entry = tk.Entry(left, width=5); p_cores_entry.pack(anchor="w")
tk.Label(left, text="E-코어 개수:").pack(anchor="w", pady=(10,0))
e_cores_entry = tk.Entry(left, width=5); e_cores_entry.pack(anchor="w")

tk.Button(left, text="초기화", command=reset_all).pack(fill="x", pady=(15,5))
tk.Button(left, text="입력 필드 생성", command=generate_input_fields).pack(fill="x", pady=5)
tk.Button(left, text="스케줄 계산", command=compute_schedule).pack(fill="x", pady=5)
tk.Button(left, text="시뮬레이션 시작", command=start_simulation).pack(fill="x", pady=5)

input_frame = tk.Frame(left)
input_frame.pack(fill="x", pady=10)

result_text = tk.Text(left, height=10)
result_text.pack(fill="both", expand=True, pady=(10,0))

# 우측: Gantt 차트
canvas = tk.Canvas(root, bg="white")
canvas.pack(side="right", fill="both", expand=True, padx=10, pady=10)

sim_label = tk.Label(root, text="시뮬레이션 대기중", font=("Arial", 12))
sim_label.pack(side="bottom", fill="x")

root.mainloop()
