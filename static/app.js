// 전역 변수
let arrivalFields = [], burstFields = [];
const timeScale = 50;
const offset = 50;
let timer = null;

// 소비전력 상수 (필요에 따라 바꾸세요)
const P_CORE_POWER = 3;
const E_CORE_POWER = 1;

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('genButton').onclick = genFields;
  document.getElementById('runButton').onclick = runFCFS;
});

function genFields(){
  const cnt = +document.getElementById('count').value;
  arrivalFields = [];
  burstFields = [];
  const c = document.getElementById('inputs');
  c.innerHTML = '';
  for(let i=0; i<cnt; i++){
    const row = document.createElement('div');
    row.style.display = 'flex';
    row.style.margin = '4px 0';
    const lbl = document.createElement('span');
    lbl.innerText = `P${i+1}`;
    lbl.style.width = '30px';
    const a = Object.assign(
      document.createElement('input'),
      { type:'number', placeholder:'arrival', style:'width:60px;' }
    );
    const b = Object.assign(
      document.createElement('input'),
      { type:'number', placeholder:'burst',   style:'width:60px;' }
    );
    arrivalFields.push(a);
    burstFields.push(b);
    row.append(lbl, a, b);
    c.append(row);
  }
}

function collectInputs(){
  return arrivalFields.map((a, i) => ({
    pid:     `P${i+1}`,
    arrival: +a.value,
    burst:   +burstFields[i].value
  }));
}

async function runFCFS() {
  const processes = collectInputs();
  const pcores = parseInt(document.getElementById('pcores').value, 10);
  const ecores = parseInt(document.getElementById('ecores').value, 10);

  const response = await fetch('/api/fcfs', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ processes, pcores, ecores })
  });
  const schedule = await response.json();

  drawGantt(schedule, pcores, ecores);
  showMetrics(schedule, processes, pcores);  // WT, TT, NTT, 소비전력 계산/표시
  animateTimeline(schedule, pcores + ecores);
}

function drawGantt(schedule, pcores, ecores) {
  const coreCount = pcores + ecores;
  const chart = document.getElementById('chart');
  chart.innerHTML = '';
  chart.style.position = 'relative';

  const xOffset = 100;
  const rowHeight = 40;
  chart.style.height = `${rowHeight * coreCount}px`;

  // 배경 줄 + 레이블
  for (let i = 0; i < coreCount; i++) {
    const rowBg = document.createElement('div');
    rowBg.style.position     = 'absolute';
    rowBg.style.top          = `${i * rowHeight}px`;
    rowBg.style.left         = '0';
    rowBg.style.width        = '100%';
    rowBg.style.height       = `${rowHeight}px`;
    rowBg.style.borderBottom = '1px solid #eee';
    chart.appendChild(rowBg);

    const label = document.createElement('div');
    label.style.position     = 'absolute';
    label.style.top          = `${i * rowHeight + rowHeight/2 - 8}px`;
    label.style.left         = '0';
    label.style.width        = '90px';
    label.style.textAlign    = 'right';
    label.style.paddingRight = '10px';
    if (i < pcores) label.textContent = `P${i+1}`;
    else            label.textContent = `E${i-pcores+1}`;
    chart.appendChild(label);
  }

  // 프로세스 바(bar)
  const xOffsetPx = 100;
  schedule.forEach(entry => {
    let idx;
    if (entry.core.startsWith('P')) {
      idx = parseInt(entry.core.slice(1), 10) - 1;
    } else {
      idx = pcores + (parseInt(entry.core.slice(1), 10) - 1);
    }
    const bar = document.createElement('div');
    bar.style.position   = 'absolute';
    bar.style.left       = `${xOffsetPx + entry.start * timeScale}px`;
    bar.style.top        = `${idx * rowHeight + 5}px`;
    bar.style.width      = `${(entry.finish - entry.start) * timeScale}px`;
    bar.style.height     = `${rowHeight - 10}px`;
    bar.style.background = entry.ctype === 'P' ? '#4f97d3' : '#d3784f';
    bar.style.border     = '1px solid #333';
    bar.style.color      = '#fff';
    bar.style.display    = 'flex';
    bar.style.alignItems = 'center';
    bar.style.justifyContent = 'center';
    bar.textContent = entry.pid;
    chart.appendChild(bar);
  });

  // 타임라인 마커
  const marker = document.getElementById('marker') || (() => {
    const m = document.createElement('div');
    m.id            = 'marker';
    m.style.position = 'absolute';
    m.style.width    = '2px';
    m.style.background = 'red';
    m.style.zIndex   = '10';
    chart.appendChild(m);
    return m;
  })();
  marker.style.height = `${rowHeight * (pcores+ecores)}px`;
  marker.style.left   = `${xOffsetPx}px`;
}

// WT, TT, NTT, 소비전력 보여주는 함수
function showMetrics(schedule, processes, pcores) {
  // 각 pid별 start, finish 찾기
  const stats = processes.map(p => ({
    pid:     p.pid,
    arrival: p.arrival,
    burst:   p.burst,
    start:   null,
    finish:  null
  }));
  schedule.forEach(e => {
    const s = stats.find(x => x.pid === e.pid);
    if (s.start === null || e.start < s.start) s.start = e.start;
    if (s.finish === null || e.finish > s.finish) s.finish = e.finish;
  });

  // 계산
  let totalPower = 0;
  stats.forEach(s => {
    s.WT  = s.start - s.arrival;
    s.TT  = s.finish - s.arrival;
    s.NTT = (s.TT / s.burst).toFixed(2);
    // schedule 항목들 중 해당 pid 것만 골라서 소비전력 계산
    schedule.filter(e => e.pid === s.pid).forEach(e => {
      const coreType = e.core.startsWith('P') ? 'P' : 'E';
      const dur = e.finish - e.start;
      totalPower += dur * (coreType === 'P' ? P_CORE_POWER : E_CORE_POWER);
    });
  });

  // 테이블 생성
  const container = document.getElementById('metrics');
  container.innerHTML = '';
  const table = document.createElement('table');
  table.style.width = '100%';
  table.style.borderCollapse = 'collapse';
  // 헤더
  const header = document.createElement('tr');
  ['PID','Arrival','Burst','Start','Finish','WT','TT','NTT','Power']
    .forEach(h => {
      const th = document.createElement('th');
      th.innerText = h;
      th.style.border = '1px solid #ccc';
      th.style.padding = '4px';
      header.appendChild(th);
    });
  table.appendChild(header);

  // 각 행
  stats.forEach(s => {
    const tr = document.createElement('tr');
    [s.pid, s.arrival, s.burst, s.start, s.finish, s.WT, s.TT, s.NTT]
      .forEach(val => {
        const td = document.createElement('td');
        td.innerText = val;
        td.style.border = '1px solid #ccc';
        td.style.padding = '4px';
        tr.appendChild(td);
      });
    // 이 프로세스 소비전력
    const power = schedule
      .filter(e=>e.pid===s.pid)
      .reduce((sum,e)=>{
        const dur = e.finish - e.start;
        const type = e.core.startsWith('P') ? P_CORE_POWER : E_CORE_POWER;
        return sum + dur*type;
      }, 0);
    const td = document.createElement('td');
    td.innerText = power;
    td.style.border = '1px solid #ccc';
    td.style.padding = '4px';
    tr.appendChild(td);

    table.appendChild(tr);
  });

  // 총합 행
  const trTotal = document.createElement('tr');
  trTotal.style.fontWeight = 'bold';
  const tdLabel = document.createElement('td');
  tdLabel.colSpan = 8;
  tdLabel.innerText = 'Total Power';
  tdLabel.style.border = '1px solid #ccc';
  tdLabel.style.padding = '4px';
  trTotal.appendChild(tdLabel);
  const tdTotal = document.createElement('td');
  tdTotal.innerText = totalPower;
  tdTotal.style.border = '1px solid #ccc';
  tdTotal.style.padding = '4px';
  trTotal.appendChild(tdTotal);
  table.appendChild(trTotal);

  container.appendChild(table);
}

function animateTimeline(schedule, coreCount) {
  if (timer) clearInterval(timer);
  const end = Math.max(...schedule.map(e => e.finish), 0);
  let t = 0;
  const wrapper = document.querySelector('main');
  const mk = document.getElementById('marker');

  timer = setInterval(() => {
    if (t > end) {
      clearInterval(timer);
      return;
    }
    const x = offset + t * timeScale;
    mk.style.left = `${x}px`;
    wrapper.scrollTo({ left: x - wrapper.clientWidth/2, behavior: 'smooth' });
    t++;
  }, 1000);
}
