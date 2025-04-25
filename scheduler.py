def fcfs_schedule_multi(processes, cores):
    procs = sorted(processes, key=lambda p: p['arrival'])
    for p in procs:
        core = min(cores, key=lambda c: c['available'])
        start = max(p['arrival'], core['available'])
        finish= start + p['burst']
        p.update(start=start, finish=finish, core=core['id'], ctype=core['type'])
        core['available'] = finish
    return procs
