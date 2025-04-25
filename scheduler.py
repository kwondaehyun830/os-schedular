# scheduler.py
import math
import heapq
import copy

def fcfs_schedule_multi(processes, cores):
    """
    FCFS 멀티코어 스케줄러
    """
    procs = sorted(processes, key=lambda p: p['arrival'])
    events = []
    total_energy = 0.0

    for p in procs:
        # 각 코어별 예상 종료 시간 계산
        candidates = []
        for c in cores:
            start = max(p['arrival'], c.get('available', 0))
            duration = math.ceil(p['burst'] / c['speed'])
            finish = start + duration
            candidates.append((finish, c, start, duration))
        # 가장 빨리 끝나는 코어
        finish, core, start, duration = min(candidates, key=lambda x: x[0])

        # 기동 전력
        if core.get('state', 'off') == 'off':
            total_energy += core['startup_power']
            core['state'] = 'on'

        # 동적 전력
        total_energy += core['dyn_power'] * duration

        # 코어 가용 시간 업데이트
        core['available'] = finish

        # 이벤트 기록
        events.append({
            'pid':    p['pid'],
            'core':   core['id'],
            'ctype':  core['type'],
            'start':  start,
            'finish': finish
        })

    return events, total_energy


def srtn_schedule_multi(processes, cores):
    """
    SRTN(Shortest Remaining Time Next) 멀티코어 스케줄러
    """
    # 준비
    remaining = {p['pid']: p['burst'] for p in processes}
    arrival  = {p['pid']: p['arrival'] for p in processes}
    pid_map   = {p['pid']: p for p in processes}

    time = 0
    done = 0
    n    = len(processes)
    events = []
    total_energy = 0.0

    # 도착순 정렬
    procs_sorted = sorted(processes, key=lambda x: x['arrival'])
    i = 0

    # 각 코어별 마지막 실행 PID 및 블록
    last_blk = {c['id']: None for c in cores}
    cur_blk  = {c['id']: None for c in cores}

    # ready 큐 (남은시간, pid)
    ready = []

    while done < n:
        # 새 도착 프로세스 추가
        while i < n and procs_sorted[i]['arrival'] <= time:
            pid = procs_sorted[i]['pid']
            heapq.heappush(ready, (remaining[pid], pid))
            i += 1

        # 각 코어에 하나씩 실행 배정
        for c in cores:
            if not ready:
                # idle 상태라면 이전 블록 마감
                if last_blk[c['id']] and cur_blk[c['id']]:
                    cur_blk[c['id']]['finish'] = time
                    events.append(cur_blk[c['id']])
                    last_blk[c['id']] = None
                    cur_blk[c['id']] = None
                continue

            rem, pid = heapq.heappop(ready)

            # 코어 기동 전력
            if c.get('state', 'off') == 'off':
                total_energy += c['startup_power']
                c['state'] = 'on'

            # 블록 전환 감지
            if last_blk[c['id']] != pid:
                # 이전 블록 마감
                if last_blk[c['id']] and cur_blk[c['id']]:
                    cur_blk[c['id']]['finish'] = time
                    events.append(cur_blk[c['id']])
                # 새 블록 시작
                cur_blk[c['id']] = {
                    'pid': pid,
                    'core': c['id'],
                    'ctype': c['type'],
                    'start': time,
                    'finish': None
                }
                last_blk[c['id']] = pid

            # 1초 실행
            remaining[pid] -= 1
            total_energy += c['dyn_power']

            # 완료 검사
            if remaining[pid] > 0:
                heapq.heappush(ready, (remaining[pid], pid))
            else:
                done += 1
                # 블록 마감
                cur_blk[c['id']]['finish'] = time + 1
                events.append(cur_blk[c['id']])
                last_blk[c['id']] = None
                cur_blk[c['id']] = None

            # 코어 가용 시간
            c['available'] = time + 1

        time += 1

    # 남은 블록 마감
    for bid in cur_blk.values():
        if bid and bid['finish'] is None:
            bid['finish'] = time
            events.append(bid)

    return events, total_energy


# 알고리즘 맵
ALGORITHMS = {
    'FCFS': fcfs_schedule_multi,
    'SRTN': srtn_schedule_multi,
}


def schedule_multi(processes, cores, policy='FCFS'):
    """
    범용 멀티코어 스케줄러 엔트리 포인트
    processes: [{'pid','arrival','burst'},...]
    cores:      [{'id','type','speed','dyn_power','startup_power','available','state'},...]
    policy:     'FCFS' 또는 'SRTN'
    반환: (events, total_energy)
    """
    if policy not in ALGORITHMS:
        raise ValueError(f"Unknown policy: {policy}")

    # 원본 훼손 방지
    cores_copy = copy.deepcopy(cores)
    return ALGORITHMS[policy](processes, cores_copy)
