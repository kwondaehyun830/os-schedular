// 버튼 클릭 시 스케줄링 실행
document.getElementById('runButton').addEventListener('click', runSchedule);

function runSchedule() {
  const procInput = document.getElementById('processes').value;
  const coreInput = document.getElementById('cores').value;
  const algo      = document.getElementById('algorithm').value;
  const url       = (algo === 'srtn') ? '/api/srtn' : '/api/fcfs';

  let payload;
  try {
    payload = {
      processes: JSON.parse(procInput),
      cores:      JSON.parse(coreInput)
    };
  } catch (e) {
    alert('JSON 파싱 오류: 올바른 포맷인지 확인하세요.');
    return;
  }

  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(data => {
    drawGantt(data.events);
    showEnergy(data.total_energy);
  })
  .catch(err => {
    console.error(err);
    alert('서버 오류가 발생했습니다.');
  });
}

// Gantt 차트 그리기
function drawGantt(events) {
  const container = document.getElementById('gantt');
  container.innerHTML = '';  // 초기화

  const scale = 40;  // 1초당 px
  events.forEach(ev => {
    const div = document.createElement('div');
    div.style.position = 'absolute';
    div.style.left = (ev.start * scale) + 'px';
    div.style.width  = ((ev.finish - ev.start) * scale) + 'px';
    div.style.height = '30px';
    div.style.background = '#87CEEB';
    div.style.border = '1px solid #000';
    div.style.lineHeight = '30px';
    div.innerText = `${ev.pid}@${ev.core}`;
    container.appendChild(div);
  });

  // 컨테이너 높이 조정
  container.style.position = 'relative';
  container.style.height = '200px';
}

// 에너지 결과 표시
function showEnergy(energy) {
  document.getElementById('energy').innerText =
    `총 에너지 소모: ${energy.toFixed(2)} W·s`;
}
