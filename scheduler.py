import math

def fcfs_schedule_multi(processes, cores):
    """
    FCFS 멀티코어 스케줄러

    입력:
    processes: [{'pid':str, 'arrival':int, 'burst':int}, ...]
    cores:     [{
                'id':str,           # ex) 'E1' or 'P2'
                'type': 'E'|'P',    # E-core or P-core
                'speed': int,       # work units per sec (E:1, P:2)
                'dyn_power': float, # W per sec (E:1, P:3)
                'startup_power': float, # W when waking from off
                'available': int,   # next available timestamp (초)
                'state': 'off'      # 'off' or 'on'
                }, ...]
    반환:
    events:       [
                    {'pid':..., 'core':..., 'ctype':..., 'start':..., 'finish':...},
                    ...
                    ]
    total_energy: float  # W·s 단위(혹은 J)
    """
    # 1) 프로세스 도착 시간 순 정렬
    procs = sorted(processes, key=lambda p: p['arrival'])
    events = []        # 각 작업을 어떤 코어에서 언제 실행했는지 기록
    total_energy = 0.0 # 누적 에너지

    for p in procs:
        # 2) 모든 코어에 대해 예상 finish time 계산
        candidates = []
        for c in cores:
            start = max(p['arrival'], c.get('available', 0))
            # 1초 단위로만 처리: 남은 burst를 코어 속도로 나눈 뒤 올림
            duration = math.ceil(p['burst'] / c['speed'])
            finish = start + duration
            candidates.append((finish, c, start, duration))

        # 3) 가장 빨리 끝나는 코어 선택
        finish, core, start, duration = min(candidates, key=lambda x: x[0])

        # 4) 시동 전력 처리
        if core.get('state', 'off') == 'off':
            total_energy += core['startup_power']
            core['state'] = 'on'

        # 5) 동적 전력 소모
        total_energy += core['dyn_power'] * duration

        # 6) 코어 가용 시간 업데이트
        core['available'] = finish

        # 7) 이벤트 기록
        events.append({
            'pid':    p['pid'],
            'core':   core['id'],
            'ctype':  core['type'],
            'start':  start,
            'finish': finish
        })

    return events, total_energy
